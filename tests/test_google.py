"""Google Sign-In: stdlib RS256 verification, JWKS caching, and the Google-only account flow."""

import base64
import hashlib
import json
import os
import secrets
import sys
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app  # noqa: E402
import google_auth as ga  # noqa: E402
import test_credits as tc  # noqa: E402

CLIENT_ID = "1234567890-test.apps.googleusercontent.com"


# --- a tiny RSA key generator for tests (Miller-Rabin; no third-party deps) ---------------
def _probable_prime(bits):
    small = (3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    while True:
        n = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if any(n % p == 0 for p in small):
            continue
        d, r = n - 1, 0
        while d % 2 == 0:
            d //= 2
            r += 1
        for _ in range(24):
            a = secrets.randbelow(n - 3) + 2
            x = pow(a, d, n)
            if x in (1, n - 1):
                continue
            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                break
        else:
            return n


def make_key(bits=2048):
    e = 65537
    while True:
        p, q = _probable_prime(bits // 2), _probable_prime(bits // 2)
        n, phi = p * q, (p - 1) * (q - 1)
        if p != q and n.bit_length() == bits and phi % e:
            return n, e, pow(e, -1, phi)


def b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64int(i: int) -> str:
    return b64(i.to_bytes((i.bit_length() + 7) // 8, "big"))


KEY = make_key()
OTHER_KEY = make_key()


def sign(header, claims, key=KEY):
    n, _e, d = key
    h = b64(json.dumps(header).encode())
    c = b64(json.dumps(claims).encode())
    k = (n.bit_length() + 7) // 8
    t = ga.SHA256_PREFIX + hashlib.sha256(f"{h}.{c}".encode()).digest()
    em = b"\x00\x01" + b"\xff" * (k - len(t) - 3) + b"\x00" + t
    sig = pow(int.from_bytes(em, "big"), d, n).to_bytes(k, "big")
    return f"{h}.{c}.{b64(sig)}"


def claims(**kw):
    now = int(time.time())
    base = {"iss": "https://accounts.google.com", "aud": CLIENT_ID, "sub": "110000000000000000001",
            "email": "namphet@gmail.com", "email_verified": True, "iat": now, "exp": now + 3600}
    base.update(kw)
    return {k: v for k, v in base.items() if v is not None}


def token(kid="k1", key=KEY, alg="RS256", **kw):
    return sign({"alg": alg, "kid": kid, "typ": "JWT"}, claims(**kw), key)


class FakeFetch:
    def __init__(self, max_age=3600):
        self.calls = 0
        self.max_age = max_age
        self.keys = {"k1": KEY}

    def __call__(self):
        self.calls += 1
        return {"keys": [{"kty": "RSA", "alg": "RS256", "use": "sig", "kid": kid, "n": b64int(k[0]), "e": b64int(k[1])}
                         for kid, k in self.keys.items()]}, self.max_age


class Verify(unittest.TestCase):
    def setUp(self):
        self.fetch = FakeFetch()
        self.keys = ga.KeyCache(self.fetch)

    def check(self, tok, **kw):
        return ga.verify_id_token(tok, CLIENT_ID, keys=self.keys, **kw)

    def test_valid_token(self):
        c = self.check(token())
        self.assertEqual((c["sub"], c["email"]), ("110000000000000000001", "namphet@gmail.com"))
        self.check(token(iss="accounts.google.com"))
        self.check(token(email_verified="true"))

    def test_rejections(self):
        bad = {
            "wrong audience": token(aud="someone-else.apps.googleusercontent.com"),
            "wrong issuer": token(iss="https://evil.example.com"),
            "expired": token(exp=int(time.time()) - 3600),
            "future": token(iat=int(time.time()) + 3600),
            "unverified email": token(email_verified=False),
            "no email": token(email=None),
            "no sub": token(sub=None),
            "other key": token(key=OTHER_KEY),
            "HS256": token(alg="HS256"),
            "none": token(alg="none"),
            "unknown kid": token(kid="nope"),
        }
        for why, tok in bad.items():
            with self.assertRaises(ga.GoogleAuthError, msg=why):
                self.check(tok)
        # Tampering with the payload breaks the signature.
        h, c, s = token().split(".")
        forged = json.loads(base64.urlsafe_b64decode(c + "=="))
        forged["email"] = "attacker@gmail.com"
        with self.assertRaises(ga.GoogleAuthError):
            self.check(f"{h}.{b64(json.dumps(forged).encode())}.{s}")
        for junk in ("", "a.b", "a.b.c", "x" * 9000, None, 123, "!!.??.**"):
            with self.assertRaises(ga.GoogleAuthError):
                self.check(junk)

    def test_jwks_cache_and_rotation(self):
        for _ in range(5):
            self.check(token())
        self.assertEqual(self.fetch.calls, 1)  # cached for max-age
        # Google rotates in a new key: unknown kid triggers one refetch.
        self.fetch.keys["k2"] = OTHER_KEY
        self.keys.last_fetch -= 120
        self.check(token(kid="k2", key=OTHER_KEY))
        self.assertEqual(self.fetch.calls, 2)
        # Unknown kids can't make us hammer Google (at most once a minute).
        for _ in range(3):
            with self.assertRaises(ga.GoogleAuthError):
                self.check(token(kid="zzz"))
        self.assertEqual(self.fetch.calls, 2)
        # After max-age the keys are refreshed.
        self.keys.expires = time.time() - 1
        self.check(token())
        self.assertEqual(self.fetch.calls, 3)

    def test_max_age_parsing_and_weak_keys(self):
        self.assertEqual(ga._max_age("public, max-age=19826, must-revalidate"), 19826)
        self.assertEqual(ga._max_age(None), 3600)
        self.assertEqual(ga._max_age("max-age=5"), 60)
        small = make_key(1024)
        self.fetch.keys["weak"] = small
        self.keys.expires = 0
        with self.assertRaises(ga.GoogleAuthError):
            self.check(token(kid="weak", key=small))


class GoogleHttp(tc.Http):
    """Runs the whole existing HTTP suite again in Google-only mode (signup() logs in with Google)."""

    def signup(self, visitor, username=None, password=None):
        sub = str(int(hashlib.sha256(visitor.encode()).hexdigest()[:15], 16))
        code, data, cookie = self.google(token(sub=sub, email=f"{(username or 'u' + visitor[:8]).lower()}@gmail.com"), visitor)
        assert code in (200, 201), (code, data)
        self.sessions[visitor] = cookie
        return data

    def setUp(self):
        super().setUp()
        self.fetch = FakeFetch()
        p1 = mock.patch.object(ga, "KEYS", ga.KeyCache(self.fetch))
        p2 = mock.patch.dict(os.environ, {"GOOGLE_CLIENT_ID": CLIENT_ID})
        p1.start()
        p2.start()
        self.addCleanup(p1.stop)
        self.addCleanup(p2.stop)

    def google(self, tok, visitor=None):
        h = {"X-Visitor-Id": visitor} if visitor else {}
        return self.raw("POST", "/api/auth/google", {"credential": tok}, h)

    def test_config_and_password_routes_closed(self):
        self.assertEqual(self.req("GET", "/api/auth/config")[1],
                         {"ok": True, "mode": "google", "googleClientId": CLIENT_ID, "uxMode": "popup"})
        for path, body in (("/api/auth/signup", {"username": "abc_def", "password": "password-1"}),
                           ("/api/auth/login", {"username": "abc_def", "password": "password-1"}),
                           ("/api/auth/password", {"current": "x", "new": "password-2"})):
            code, data, _ = self.raw("POST", path, body, {"X-Visitor-Id": "a" * 32})
            self.assertEqual((code, data["code"]), (403, "google_only"), path)
        code, data, _ = self.raw("POST", "/api/admin/reset-password", {"username": "x"}, self.ADMIN)
        self.assertEqual(code, 403)

    def test_google_login_merge_free_question_and_admin(self):
        vid = "g" * 32
        # Anonymous paid credits (bought before accounts) + a pending order follow the first Google login.
        tc_give = __import__("test_accounts")._give
        tc_give(app.SERVICE, vid, 4, free_used=True)
        pending = app.SERVICE.create_order(vid, 15)
        code, data, ck = self.google(token(), vid)
        self.assertEqual(code, 201)
        self.assertIn("HttpOnly", ck)
        self.assertIn("Secure", ck)
        self.assertEqual(data["account"], {"username": "namphet@gmail.com", "google": True})
        self.assertEqual((data["merged"]["movedCredits"], data["merged"]["movedOrders"]), (4, 1))
        self.assertEqual((data["credits"], data["freeAvailable"]), (4, True))  # 1 free question per Google account
        cookie = ck.split(";")[0]
        h = {"X-Visitor-Id": vid, "Cookie": cookie}
        body = {"name": "น้ำเพชร", "topic": "love", "lang": "th"}
        kinds = [self.raw("POST", "/api/reading", body, h)[1]["charge"]["kind"] for _ in range(5)]
        self.assertEqual(kinds, ["paid"] * 4 + ["free"])  # paid credits first, then the one free question
        code, r, _ = self.raw("POST", "/api/reading", body, h)
        self.assertEqual((code, r["code"]), (402, "no_credits"))
        # Same Google account on another device (email changed): same wallet, no second free question.
        code, data, ck2 = self.google(token(email="NamPhet.New@gmail.com"), "h" * 32)
        self.assertEqual(code, 200)
        self.assertEqual((data["account"]["username"], data["credits"], data["freeAvailable"]),
                         ("namphet.new@gmail.com", 0, False))
        # A different Google account is a different wallet with its own free question.
        code, data, _ = self.google(token(sub="220000000000000000002", email="friend@gmail.com"), "i" * 32)
        self.assertEqual((code, data["credits"], data["freeAvailable"]), (201, 0, True))
        # Admin: accounts by email, orders show the email.
        users = self.raw("GET", "/api/admin/users", None, self.ADMIN)[1]
        self.assertEqual(users["mode"], "google")
        self.assertEqual({u["email"] for u in users["users"]}, {"namphet.new@gmail.com", "friend@gmail.com"})
        self.assertTrue(all(u["kind"] == "google" for u in users["users"]))
        orders = self.raw("GET", "/api/admin/orders", None, self.ADMIN)[1]["orders"]
        self.assertEqual(next(o for o in orders if o["code"] == pending["code"])["email"], "namphet.new@gmail.com")
        self.assertEqual(self.raw("GET", "/api/admin/users", None, {})[0], 401)

    def test_bad_tokens_rejected(self):
        for tok in (token(aud="other"), token(key=OTHER_KEY), token(email_verified=False), "garbage", None):
            code, data, ck = self.google(tok, "j" * 32)
            self.assertEqual((code, data["code"]), (401, "bad_google_token"))
            self.assertIsNone(ck)

    def form_post(self, path, fields, cookie=None):
        import http.client
        import urllib.parse
        host, port = self.base.replace("http://", "").split(":")
        conn = http.client.HTTPConnection(host, int(port), timeout=10)
        body = urllib.parse.urlencode(fields)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if cookie:
            headers["Cookie"] = cookie
        conn.request("POST", path, body, headers)
        res = conn.getresponse()
        res.read()
        out = (res.status, res.getheader("Location"), res.getheader("Set-Cookie"))
        conn.close()
        return out

    def test_redirect_mode_login(self):
        with mock.patch.dict(os.environ, {"GOOGLE_UX_MODE": "redirect"}):
            self.assertEqual(self.req("GET", "/api/auth/config")[1]["uxMode"], "redirect")
        path = "/api/auth/google/redirect"
        # CSRF: Google's double-submit token must be in both the cookie and the form.
        self.assertEqual(self.form_post(path, {"credential": token(), "g_csrf_token": "abc"})[:2], (303, "/?login=failed"))
        self.assertEqual(self.form_post(path, {"credential": token(), "g_csrf_token": "abc"}, "g_csrf_token=xyz")[:2],
                         (303, "/?login=failed"))
        code, loc, ck = self.form_post(path, {"credential": token(aud="other"), "g_csrf_token": "abc"}, "g_csrf_token=abc")
        self.assertEqual((code, loc, ck), (303, "/?login=failed", None))
        code, loc, ck = self.form_post(path, {"credential": token(), "g_csrf_token": "abc"}, "other=1; g_csrf_token=abc")
        self.assertEqual((code, loc), (303, "/?login=done"))
        self.assertIn("HttpOnly", ck)
        cookie = ck.split(";")[0]
        # Back on the site, the page merges this browser's guest credits into the account.
        vid = "m" * 32
        __import__("test_accounts")._give(app.SERVICE, vid, 3, free_used=True)
        code, data, _ = self.raw("POST", "/api/auth/merge", {}, {"X-Visitor-Id": vid, "Cookie": cookie})
        self.assertEqual(code, 200)
        self.assertEqual(data["account"]["username"], "namphet@gmail.com")
        self.assertEqual((data["merged"]["movedCredits"], data["credits"]), (3, 3))
        self.assertEqual(self.raw("POST", "/api/auth/merge", {}, {"X-Visitor-Id": vid})[0], 401)

    def test_google_user_cannot_be_reached_by_password_login(self):
        self.google(token(), "k" * 32)
        with mock.patch.dict(os.environ, {"GOOGLE_CLIENT_ID": ""}):
            code, data, _ = self.raw("POST", "/api/auth/login",
                                     {"username": "google:110000000000000000001", "password": "!google"}, {})
            self.assertEqual(code, 401)


class PasswordModeStillWorks(tc.Http):
    def test_without_client_id(self):
        with mock.patch.dict(os.environ, {"GOOGLE_CLIENT_ID": ""}):
            self.assertEqual(self.req("GET", "/api/auth/config")[1]["mode"], "password")
            code, data, _ = self.raw("POST", "/api/auth/google", {"credential": token()}, {})
            self.assertEqual((code, data["code"]), (503, "google_disabled"))
            code, _, _ = self.raw("POST", "/api/auth/signup", {"username": "still_ok", "password": "password-1"},
                                  {"X-Visitor-Id": "l" * 32})
            self.assertEqual(code, 201)


@unittest.skipUnless(tc.TEST_PG, "set TEST_DATABASE_URL to run against Postgres")
class PgGoogleHttp(GoogleHttp):
    make = staticmethod(tc.pg_service)


if __name__ == "__main__":
    unittest.main()
