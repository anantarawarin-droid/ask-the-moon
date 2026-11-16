"""Accounts: sign-up, login, sessions, merge, purchases, admin reset."""

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import accounts  # noqa: E402
import app  # noqa: E402
import test_credits as tc  # noqa: E402

V1, V2 = "c" * 32, "d" * 32


class Hashing(unittest.TestCase):
    def test_pbkdf2_record(self):
        rec = accounts.hash_password("correct horse")
        algo, iters, salt, digest = rec.split("$")
        self.assertEqual(algo, "pbkdf2_sha256")
        self.assertGreaterEqual(int(iters), 200_000)
        self.assertEqual(len(bytes.fromhex(salt)), 16)
        self.assertTrue(accounts.verify_password("correct horse", rec))
        self.assertFalse(accounts.verify_password("correct horsE", rec))
        self.assertNotEqual(rec, accounts.hash_password("correct horse"))  # per-user salt
        self.assertFalse(accounts.verify_password("x", "garbage"))

    def test_username_rules(self):
        for ok in ("abc", "Nam_Phet_99", "a" * 20):
            self.assertEqual(accounts.validate_username(ok), ok)
        for bad in ("ab", "a" * 21, "nam phet", "น้ำเพชร", "a-b", ""):
            with self.assertRaises(accounts.AuthError):
                accounts.validate_username(bad)
        with self.assertRaises(accounts.AuthError):
            accounts.validate_password("short7!")

    def test_cookie_flags(self):
        ck = accounts.session_cookie("tok")
        for flag in ("HttpOnly", "Secure", "SameSite=Lax", "Path=/", f"Max-Age={90 * 86400}"):
            self.assertIn(flag, ck)


class AccountHttp(tc.Http):
    def auth(self, path, username, password, visitor=None, cookie=None):
        h = {}
        if visitor:
            h["X-Visitor-Id"] = visitor
        if cookie:
            h["Cookie"] = cookie
        return self.raw("POST", path, {"username": username, "password": password}, h)

    def me(self, cookie=None, visitor=V1):
        h = {"X-Visitor-Id": visitor}
        if cookie:
            h["Cookie"] = cookie
        return self.raw("GET", "/api/auth/me", None, h)[1]

    def test_signup_login_logout(self):
        code, data, ck = self.auth("/api/auth/signup", "NamPhet", "moonlight-88", V1)
        self.assertEqual(code, 201)
        self.assertEqual(data["account"], {"username": "NamPhet"})
        self.assertIn("HttpOnly", ck)
        cookie = ck.split(";")[0]
        self.assertEqual(self.me(cookie)["account"]["username"], "NamPhet")
        # Wrong password, unknown user: same generic error.
        self.assertEqual(self.auth("/api/auth/login", "namphet", "wrong-pass-1")[1]["code"], "bad_login")
        self.assertEqual(self.auth("/api/auth/login", "nobody_here", "wrong-pass-1")[1]["code"], "bad_login")
        # Case-insensitive login works and gives a new session.
        code, data, ck2 = self.auth("/api/auth/login", "NAMPHET", "moonlight-88", V2)
        self.assertEqual(code, 200)
        cookie2 = ck2.split(";")[0]
        self.assertNotEqual(cookie, cookie2)
        # Logout ends only that session.
        code, data, ck3 = self.raw("POST", "/api/auth/logout", {}, {"Cookie": cookie2, "X-Visitor-Id": V2})
        self.assertEqual(code, 200)
        self.assertIn("Max-Age=0", ck3)
        self.assertIsNone(self.me(cookie2, V2)["account"])
        self.assertEqual(self.me(cookie)["account"]["username"], "NamPhet")

    def test_duplicate_username_case_insensitive(self):
        self.assertEqual(self.auth("/api/auth/signup", "moon_cat", "password-1", V1)[0], 201)
        code, data, _ = self.auth("/api/auth/signup", "Moon_Cat", "password-2", V2)
        self.assertEqual((code, data["code"]), (409, "username_taken"))
        self.assertEqual(self.auth("/api/auth/signup", "x!", "password-2", V2)[1]["code"], "bad_username")
        self.assertEqual(self.auth("/api/auth/signup", "okname", "short", V2)[1]["code"], "weak_password")

    def test_session_expiry(self):
        _, _, ck = self.auth("/api/auth/signup", "expiring", "password-1", V1)
        cookie = ck.split(";")[0]
        token = cookie.split("=", 1)[1]
        user = app.SERVICE.find_user("expiring")
        # A session that expired yesterday is ignored.
        app.SERVICE.delete_session(accounts.token_hash(token))
        app.SERVICE.create_session(user["id"], accounts.token_hash(token),
                                   datetime.now(timezone.utc) - timedelta(days=1))
        self.assertIsNone(self.me(cookie)["account"])
        self.assertEqual(accounts.SESSION_DAYS, 90)

    def test_login_rate_limit(self):
        self.auth("/api/auth/signup", "target_1", "password-1", V1)
        codes = [self.auth("/api/auth/login", "target_1", f"guess-{i:04d}")[0] for i in range(12)]
        self.assertEqual(codes[:10], [401] * 10)
        self.assertEqual(codes[10:], [429, 429])
        # Even the right password is refused while limited.
        self.assertEqual(self.auth("/api/auth/login", "target_1", "password-1")[0], 429)

    def test_signup_rate_limit(self):
        codes = [self.auth("/api/auth/signup", f"spam_{i}", "password-1", ("e%031d" % i))[0] for i in range(7)]
        self.assertEqual(codes[:5], [201] * 5)
        self.assertEqual(codes[5:], [429, 429])

    def test_purchase_requires_login(self):
        code, data, _ = self.raw("POST", "/api/orders", {"amount": 15}, {"X-Visitor-Id": V1})
        self.assertEqual((code, data["code"]), (401, "login_required"))
        # Free question still works anonymously.
        code, data, _ = self.raw("POST", "/api/reading", {"name": "น้ำเพชร", "topic": "love", "lang": "th"},
                                 {"X-Visitor-Id": V1})
        self.assertEqual((code, data["charge"]["kind"]), (200, "free"))

    def test_merge_is_idempotent_and_orders_follow(self):
        # Anonymous visitor with 3 credits (e.g. bought before accounts existed), free used, and a pending order.
        _give(app.SERVICE, V1, 3, free_used=True)
        anon_order = app.SERVICE.create_order(V1, 30)
        code, data, ck = self.auth("/api/auth/signup", "merge_me", "password-1", V1)
        self.assertEqual(code, 201)
        self.assertEqual(data["merged"]["movedCredits"], 3)
        self.assertEqual((data["credits"], data["freeAvailable"]), (3, False))
        # Login again from the same device: nothing moves twice.
        code, data, ck2 = self.auth("/api/auth/login", "merge_me", "password-1", V1)
        self.assertEqual((data["merged"]["movedCredits"], data["credits"]), (0, 3))
        # The visitor itself is now empty, so logging out can't double-spend.
        self.assertEqual(app.SERVICE.balance(V1), {"credits": 0, "freeAvailable": False})
        # The pending order now belongs to the account; approving credits the account.
        self.req("POST", f"/api/admin/orders/{anon_order['code']}/approve", {}, self.ADMIN)
        self.assertEqual(self.me(ck2.split(";")[0])["credits"], 5)
        # Admin sees the username on the order.
        _, adm, _ = self.raw("GET", "/api/admin/orders", None, self.ADMIN)
        o = next(x for x in adm["orders"] if x["code"] == anon_order["code"])
        self.assertEqual(o["username"], "merge_me")

    def test_free_question_carries_over_once(self):
        # Unused free question moves into the account; the device can't get another one after logout.
        code, data, ck = self.auth("/api/auth/signup", "freebie", "password-1", V1)
        self.assertTrue(data["freeAvailable"])
        cookie = ck.split(";")[0]
        r = self.raw("POST", "/api/reading", {"name": "A", "topic": "love", "lang": "th"},
                     {"X-Visitor-Id": V1, "Cookie": cookie})[1]
        self.assertEqual(r["charge"]["kind"], "free")
        code, r, _ = self.raw("POST", "/api/reading", {"name": "A", "topic": "love", "lang": "th"}, {"X-Visitor-Id": V1})
        self.assertEqual(code, 402)

    def test_buy_and_deduct_on_account_across_devices(self):
        _, _, ck = self.auth("/api/auth/signup", "buyer_01", "password-1", V1)
        cookie = ck.split(";")[0]
        code, data, _ = self.raw("POST", "/api/orders", {"amount": 45}, {"X-Visitor-Id": V1, "Cookie": cookie})
        self.assertEqual(code, 200)
        self.req("POST", f"/api/admin/orders/{data['order']['code']}/approve", {}, self.ADMIN)
        # Another device logs in and sees the same balance.
        _, d2, ck2 = self.auth("/api/auth/login", "buyer_01", "password-1", V2)
        self.assertEqual(d2["credits"], 3)
        cookie2 = ck2.split(";")[0]
        r = self.raw("POST", "/api/reading", {"name": "A", "topic": "career", "lang": "th"},
                     {"X-Visitor-Id": V2, "Cookie": cookie2})[1]
        # First reading on this account uses the free question (still unused); then paid ones deduct.
        r = self.raw("POST", "/api/reading", {"name": "A", "topic": "career", "lang": "th"},
                     {"X-Visitor-Id": V2, "Cookie": cookie2})[1]
        self.assertEqual(r["charge"]["kind"], "paid")
        self.assertEqual(self.me(cookie)["credits"], r["balance"]["credits"])
        self.assertEqual(r["account"], {"username": "buyer_01"})
        # The account's wallet id can't be used as a visitor header.
        acct = app.SERVICE.find_user("buyer_01")["id"]
        code, _, _ = self.raw("POST", "/api/reading", {"name": "A", "topic": "career", "lang": "th"},
                              {"X-Visitor-Id": acct})
        self.assertEqual(code, 400)
        self.assertNotIn(acct, repr(r))

    def test_admin_reset_password_and_change(self):
        _, _, ck = self.auth("/api/auth/signup", "forgetful", "password-1", V1)
        code, data, _ = self.raw("POST", "/api/admin/reset-password", {"username": "FORGETFUL"}, {})
        self.assertEqual(code, 401)
        code, data, _ = self.raw("POST", "/api/admin/reset-password", {"username": "FORGETFUL"}, self.ADMIN)
        self.assertEqual(code, 200)
        temp = data["tempPassword"]
        self.assertIsNone(self.me(ck.split(";")[0])["account"])  # old sessions ended
        self.assertEqual(self.auth("/api/auth/login", "forgetful", "password-1")[0], 401)
        code, _, ck2 = self.auth("/api/auth/login", "forgetful", temp)
        self.assertEqual(code, 200)
        cookie2 = ck2.split(";")[0]
        code, _, ck3 = self.raw("POST", "/api/auth/password", {"current": temp, "new": "brand-new-pass"},
                                {"Cookie": cookie2})
        self.assertEqual(code, 200)
        self.assertEqual(self.auth("/api/auth/login", "forgetful", "brand-new-pass")[0], 200)
        self.assertEqual(self.raw("POST", "/api/admin/reset-password", {"username": "ghost"}, self.ADMIN)[0], 404)


def _give(service, visitor, credits, free_used=False):
    if hasattr(service, "store"):
        with service.store.transaction() as data:
            data["visitors"][visitor] = {"credits": credits, "freeUsed": free_used, "createdAt": "x"}
    else:
        with service._tx() as cur:
            cur.execute("INSERT INTO moon_visitors (id, credits, free_used) VALUES (%s, %s, %s) "
                        "ON CONFLICT (id) DO UPDATE SET credits = EXCLUDED.credits, free_used = EXCLUDED.free_used",
                        (visitor, credits, free_used))


@unittest.skipUnless(tc.TEST_PG, "set TEST_DATABASE_URL to run against Postgres")
class PgAccountHttp(AccountHttp):
    make = staticmethod(tc.pg_service)


if __name__ == "__main__":
    unittest.main()
