"""Verify Google Sign-In ID tokens with the standard library only.

* Google's public keys (JWKS) are fetched from GOOGLE_CERTS_URL and cached for
  the Cache-Control max-age (refetched at most once a minute on an unknown key id).
* RS256 = RSASSA-PKCS1-v1_5 with SHA-256, checked with pow() and a constant-time compare.
* Claims: aud == GOOGLE_CLIENT_ID, iss is Google, exp/iat sane, email_verified, sub present.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import threading
import time
import urllib.request
from typing import Any, Callable

GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"
ISSUERS = {"accounts.google.com", "https://accounts.google.com"}
LEEWAY = 60  # seconds of clock skew allowed
MAX_TOKEN_BYTES = 8192
# DER prefix of DigestInfo for SHA-256 (RFC 8017 §9.2 note 1)
SHA256_PREFIX = bytes.fromhex("3031300d060960864801650304020105000420")


class GoogleAuthError(Exception):
    """The token is not a valid Google ID token for this site."""


def client_id() -> str | None:
    value = (os.environ.get("GOOGLE_CLIENT_ID") or "").strip()
    return value or None


def b64url_decode(data: str) -> bytes:
    if not isinstance(data, str) or not re.fullmatch(r"[A-Za-z0-9_-]*", data):
        raise GoogleAuthError("bad base64url")
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def _int(data: str) -> int:
    return int.from_bytes(b64url_decode(data), "big")


def rsa_pkcs1v15_sha256_verify(message: bytes, signature: bytes, n: int, e: int) -> bool:
    k = (n.bit_length() + 7) // 8
    if k < 256 or len(signature) != k:  # Google uses 2048-bit keys; refuse anything weaker
        return False
    s = int.from_bytes(signature, "big")
    if s >= n:
        return False
    em = pow(s, e, n).to_bytes(k, "big")
    t = SHA256_PREFIX + hashlib.sha256(message).digest()
    if k < len(t) + 11:
        return False
    expected = b"\x00\x01" + b"\xff" * (k - len(t) - 3) + b"\x00" + t
    return hmac.compare_digest(em, expected)


def _max_age(cache_control: str | None) -> int:
    m = re.search(r"max-age=(\d+)", cache_control or "")
    return max(60, min(int(m.group(1)), 86400)) if m else 3600


def _default_fetch() -> tuple[dict[str, Any], int]:
    req = urllib.request.Request(GOOGLE_CERTS_URL, headers={"User-Agent": "AskTheMoon/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=6) as resp:  # noqa: S310 (fixed https URL)
        body = json.loads(resp.read(200_000).decode("utf-8"))
        return body, _max_age(resp.headers.get("Cache-Control"))


class KeyCache:
    def __init__(self, fetch: Callable[[], tuple[dict[str, Any], int]] = _default_fetch):
        self.fetch = fetch
        self.lock = threading.Lock()
        self.keys: dict[str, tuple[int, int]] = {}
        self.expires = 0.0
        self.last_fetch = 0.0

    def _refresh(self) -> None:
        jwks, max_age = self.fetch()
        keys = {}
        for k in jwks.get("keys", []):
            if k.get("kty") == "RSA" and k.get("kid") and k.get("n") and k.get("e") and k.get("alg", "RS256") == "RS256":
                keys[k["kid"]] = (_int(k["n"]), _int(k["e"]))
        if not keys:
            raise GoogleAuthError("Google returned no usable keys")
        now = time.time()
        self.keys, self.expires, self.last_fetch = keys, now + max_age, now

    def get(self, kid: str) -> tuple[int, int]:
        with self.lock:
            now = time.time()
            if now >= self.expires or (kid not in self.keys and now - self.last_fetch > 60):
                try:
                    self._refresh()
                except GoogleAuthError:
                    raise
                except Exception as exc:  # network trouble: keep using cached keys if any
                    if not self.keys:
                        raise GoogleAuthError("Could not load Google's signing keys") from exc
            if kid not in self.keys:
                raise GoogleAuthError("unknown key id")
            return self.keys[kid]


KEYS = KeyCache()


def verify_id_token(token: Any, audience: str, keys: KeyCache | None = None, now: float | None = None) -> dict[str, Any]:
    """Return the verified claims, or raise GoogleAuthError."""
    if not isinstance(token, str) or not token or len(token) > MAX_TOKEN_BYTES:
        raise GoogleAuthError("missing token")
    parts = token.split(".")
    if len(parts) != 3:
        raise GoogleAuthError("malformed token")
    try:
        header = json.loads(b64url_decode(parts[0]))
        claims = json.loads(b64url_decode(parts[1]))
        signature = b64url_decode(parts[2])
    except (ValueError, UnicodeDecodeError) as exc:
        raise GoogleAuthError("malformed token") from exc
    if not isinstance(header, dict) or not isinstance(claims, dict):
        raise GoogleAuthError("malformed token")
    if header.get("alg") != "RS256" or not isinstance(header.get("kid"), str):
        raise GoogleAuthError("unsupported algorithm")
    n, e = (keys or KEYS).get(header["kid"])
    if not rsa_pkcs1v15_sha256_verify(f"{parts[0]}.{parts[1]}".encode("ascii"), signature, n, e):
        raise GoogleAuthError("bad signature")
    now = time.time() if now is None else now
    aud = claims.get("aud")
    if not audience or not (aud == audience or (isinstance(aud, list) and audience in aud)):
        raise GoogleAuthError("wrong audience")
    if claims.get("iss") not in ISSUERS:
        raise GoogleAuthError("wrong issuer")
    exp, iat = claims.get("exp"), claims.get("iat", 0)
    if not isinstance(exp, (int, float)) or exp + LEEWAY < now:
        raise GoogleAuthError("token expired")
    if isinstance(iat, (int, float)) and iat - LEEWAY > now:
        raise GoogleAuthError("token from the future")
    if claims.get("email_verified") not in (True, "true"):
        raise GoogleAuthError("email not verified")
    sub, email = claims.get("sub"), claims.get("email")
    if not isinstance(sub, str) or not re.fullmatch(r"[0-9A-Za-z_-]{1,255}", sub):
        raise GoogleAuthError("missing subject")
    if not isinstance(email, str) or "@" not in email or len(email) > 254:
        raise GoogleAuthError("missing email")
    return claims
