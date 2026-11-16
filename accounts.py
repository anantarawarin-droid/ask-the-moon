"""Username + password accounts: hashing, validation, sessions, and rate limits.

Passwords: PBKDF2-HMAC-SHA256 with a per-user random salt, compared in constant time.
Sessions: a random token in an HttpOnly/Secure/SameSite=Lax cookie; only its SHA-256
is stored server-side. An account's credits live in a wallet row whose id is the
account id ("acct_..."), which is never sent to the browser.
"""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import string
from datetime import datetime, timedelta, timezone

from slips import VisitorLimiter

PBKDF2_ITERATIONS = 240_000
SESSION_DAYS = 90
COOKIE_NAME = "moon_session"
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")
MIN_PASSWORD = 8
MAX_PASSWORD = 128
ACCOUNT_PREFIX = "acct_"

# In-memory rate limits (reset on restart).
LOGIN_BY_IP = VisitorLimiter(limit=20, window=600)
LOGIN_BY_USER = VisitorLimiter(limit=10, window=600)
SIGNUP_BY_IP = VisitorLimiter(limit=5, window=3600)
SIGNUP_GLOBAL = VisitorLimiter(limit=200, window=3600)


class AuthError(Exception):
    def __init__(self, message: str, status: int, code: str):
        super().__init__(message)
        self.status = status
        self.code = code


def username_key(username: str) -> str:
    return username.strip().lower()


def validate_username(username: object) -> str:
    name = str(username or "").strip()
    if not USERNAME_RE.match(name):
        raise AuthError("Username must be 3–20 letters, numbers, or _.", 400, "bad_username")
    return name


def validate_password(password: object) -> str:
    pw = str(password or "")
    if len(pw) < MIN_PASSWORD:
        raise AuthError("Password must be at least 8 characters.", 400, "weak_password")
    if len(pw) > MAX_PASSWORD:
        raise AuthError("Password is too long.", 400, "bad_password")
    return pw


def hash_password(password: str, iterations: int | None = None) -> str:
    iterations = iterations or PBKDF2_ITERATIONS
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}"


def verify_password(password: str, record: str | None) -> bool:
    try:
        algo, iters, salt_hex, hash_hex = str(record).split("$")
        if algo != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iters))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(digest.hex(), hash_hex)


# Used so a login for an unknown username costs the same time as a real one.
_DUMMY_RECORD = hash_password(secrets.token_hex(8), 1000)


def burn_time(password: str) -> None:
    algo, _iters, salt_hex, _ = _DUMMY_RECORD.split("$")
    hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), PBKDF2_ITERATIONS)


def new_account_id() -> str:
    return ACCOUNT_PREFIX + secrets.token_hex(12)


def is_account_id(value: str | None) -> bool:
    return bool(value) and str(value).startswith(ACCOUNT_PREFIX)


def new_session_token() -> str:
    return secrets.token_urlsafe(32)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def session_expiry(now: datetime | None = None) -> datetime:
    return (now or datetime.now(timezone.utc)) + timedelta(days=SESSION_DAYS)


def session_cookie(token: str) -> str:
    return (f"{COOKIE_NAME}={token}; Path=/; Max-Age={SESSION_DAYS * 86400}; "
            "HttpOnly; Secure; SameSite=Lax")


def clear_cookie() -> str:
    return f"{COOKIE_NAME}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax"


def read_cookie(header: str | None) -> str | None:
    for part in (header or "").split(";"):
        name, _, value = part.strip().partition("=")
        if name == COOKIE_NAME and value:
            return value.strip()
    return None


_TEMP_ALPHABET = "".join(c for c in string.ascii_letters + string.digits if c not in "0OolI1")


def temp_password() -> str:
    """A readable temporary password the admin can send on LINE."""
    raw = "".join(secrets.choice(_TEMP_ALPHABET) for _ in range(10))
    return f"{raw[:5]}-{raw[5:]}"
