"""Tests for pricing, PromptPay payloads, orders, and credit deduction.

Run: python3 -m unittest discover -s tests -v
"""

import io
import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="moon-test-"))

import app  # noqa: E402
import credits as billing  # noqa: E402

EXPECTED = {  # price: (questions, bonus, avg)
    15: (1, 0, "15.00"), 30: (2, 0, "15.00"), 45: (3, 0, "15.00"),
    60: (4, 0, "15.00"), 75: (5, 0, "15.00"), 90: (7, 1, "12.86"),
    105: (8, 1, "13.13"), 120: (10, 2, "12.00"), 135: (12, 3, "11.25"),
    150: (15, 5, "10.00"),
}
VISITOR = "a" * 32
OTHER = "b" * 32


TEST_PG = os.environ.get("TEST_DATABASE_URL")  # e.g. postgresql://postgres@127.0.0.1:54329/moontest?sslmode=disable
_PG = None


def json_service():
    return billing.CreditService(billing.JsonStore(tempfile.mkdtemp(prefix="moon-")))


def pg_service():
    global _PG
    if _PG is None:
        _PG = billing.PostgresCreditService(TEST_PG)
    with _PG._tx() as cur:
        cur.execute("TRUNCATE moon_visitors, moon_orders, moon_sessions, moon_users")
    return _PG


fresh_service = json_service


class PackageTable(unittest.TestCase):
    def test_exact_table(self):
        got = {p["price"]: (p["questions"], p["bonus"], p["perQuestion"]) for p in billing.PACKAGES}
        self.assertEqual(got, EXPECTED)
        self.assertEqual([p["price"] for p in billing.PACKAGES], list(range(15, 151, 15)))

    def test_max_and_best_value(self):
        self.assertEqual(billing.MAX_AMOUNT, 150)
        self.assertTrue(all(p["price"] <= 150 for p in billing.PACKAGES))
        best = [p for p in billing.PACKAGES if p["bestValue"]]
        self.assertEqual(len(best), 1)
        self.assertEqual((best[0]["price"], best[0]["questions"], best[0]["bonus"], best[0]["perQuestion"]),
                         (150, 15, 5, "10.00"))

    def test_bonus_never_decreases(self):
        bonuses = [p["bonus"] for p in billing.PACKAGES]
        self.assertEqual(bonuses, sorted(bonuses))

    def test_invalid_amounts(self):
        for bad in (0, 1, 14, 16, 100, 165, 300, -15, 15.5, "abc", None, True, [], "", "150.5"):
            with self.assertRaises(ValueError, msg=repr(bad)):
                billing.package_for_amount(bad)
        self.assertEqual(billing.package_for_amount("150")["questions"], 15)
        self.assertEqual(billing.package_for_amount(90.0)["questions"], 7)


class PromptPay(unittest.TestCase):
    def test_crc_check_value(self):
        # Standard CRC-16/CCITT-FALSE check value.
        self.assertEqual(billing.crc16_ccitt("123456789"), "29B1")

    def test_reference_payloads(self):
        # From the promptpay-qr npm package (dtinth) — the README example and
        # outputs generated with v0.5.0.
        cases = [
            ("000-000-0000", 4.22,
             "00020101021229370016A000000677010111011300660000000005802TH530376454044.226304E469"),
            ("0812345678", 150,
             "00020101021229370016A000000677010111011300668123456785802TH53037645406150.006304CC46"),
            ("0812345678", 12.5,
             "00020101021229370016A000000677010111011300668123456785802TH5303764540512.506304C900"),
            ("1234567890123", 90,
             "00020101021229370016A000000677010111021312345678901235802TH5303764540590.006304083C"),
            ("0812345678", None,
             "00020101021129370016A000000677010111011300668123456785802TH530376463045D82"),
        ]
        for pid, amount, expected in cases:
            self.assertEqual(billing.promptpay_payload(pid, amount), expected, (pid, amount))

    def test_bad_id(self):
        with self.assertRaises(ValueError):
            billing.promptpay_payload("12345", 15)


class Orders(unittest.TestCase):
    make = staticmethod(json_service)

    def setUp(self):
        self.svc = self.make()

    def test_order_approve_balance_and_idempotent(self):
        for price, (questions, _bonus, _avg) in EXPECTED.items():
            svc = self.make()
            order = svc.create_order(VISITOR, price)
            self.assertEqual(order["status"], "pending")
            self.assertEqual(svc.balance(VISITOR)["credits"], 0)
            first = svc.approve(order["code"])
            self.assertFalse(first["alreadyApproved"])
            self.assertEqual(svc.balance(VISITOR)["credits"], questions)
            again = svc.approve(order["code"])
            self.assertTrue(again["alreadyApproved"])
            self.assertEqual(svc.balance(VISITOR)["credits"], questions)

    def test_revoke_takes_back_unused_credits_once(self):
        order = self.svc.create_order(VISITOR, 45)  # 3 questions
        self.svc.approve(order["code"])
        res = self.svc.revoke(order["code"].lower())
        self.assertEqual((res["removed"], res["credits"], res["alreadyRevoked"]), (3, 0, False))
        self.assertEqual(res["order"]["status"], "rejected")
        self.assertIsNotNone(res["order"]["revokedAt"])
        self.assertEqual(res["order"]["revokedCredits"], 3)
        self.assertEqual(self.svc.balance(VISITOR)["credits"], 0)
        again = self.svc.revoke(order["code"])
        self.assertEqual((again["removed"], again["alreadyRevoked"]), (0, True))
        # A revoked order can't be approved again (no double credit).
        with self.assertRaises(billing.PaymentError) as ctx:
            self.svc.approve(order["code"])
        self.assertEqual(ctx.exception.code, "not_pending")
        self.assertEqual(self.svc.balance(VISITOR)["credits"], 0)
        listed = {o["code"]: o for o in self.svc.list_orders("rejected")}
        self.assertEqual(listed[order["code"]]["revokedCredits"], 3)

    def test_revoke_never_goes_below_zero_and_keeps_other_orders(self):
        a = self.svc.create_order(VISITOR, 45)  # 3
        self.svc.approve(a["code"])
        self.svc.reserve_reading(VISITOR)  # used 1 paid credit -> 2 left
        self.svc.reserve_reading(VISITOR)  # -> 1 left
        res = self.svc.revoke(a["code"])
        self.assertEqual((res["removed"], res["credits"]), (1, 0))
        self.assertEqual(self.svc.balance(VISITOR)["credits"], 0)
        b = self.svc.create_order(VISITOR, 15)  # 1
        c = self.svc.create_order(VISITOR, 30)  # 2
        self.svc.approve(b["code"]); self.svc.approve(c["code"])
        self.assertEqual(self.svc.balance(VISITOR)["credits"], 3)
        res = self.svc.revoke(b["code"])
        self.assertEqual((res["removed"], res["credits"]), (1, 2))
        self.assertEqual({o["code"]: o["status"] for o in self.svc.list_orders()}[c["code"]], "approved")

    def test_revoke_only_approved_orders(self):
        order = self.svc.create_order(VISITOR, 15)
        with self.assertRaises(billing.PaymentError) as ctx:
            self.svc.revoke(order["code"])
        self.assertEqual((ctx.exception.status, ctx.exception.code), (409, "not_approved"))
        self.svc.reject(order["code"])
        with self.assertRaises(billing.PaymentError) as ctx:
            self.svc.revoke(order["code"])
        self.assertEqual(ctx.exception.code, "not_approved")
        with self.assertRaises(billing.PaymentError) as ctx:
            self.svc.revoke("MZZZZZ")
        self.assertEqual(ctx.exception.status, 404)

    def test_revoke_follows_merged_wallet(self):
        order = self.svc.create_order(OTHER, 30)  # 2
        self.svc.approve(order["code"])
        account = "e" * 32
        self.svc.merge_visitor(OTHER, account)
        self.assertEqual(self.svc.balance(account)["credits"], 2)
        res = self.svc.revoke(order["code"])
        self.assertEqual((res["removed"], res["credits"]), (2, 0))
        self.assertEqual(self.svc.balance(account)["credits"], 0)

    def test_concurrent_revoke_takes_back_once(self):
        order = self.svc.create_order(VISITOR, 45)
        self.svc.approve(order["code"])
        extra = self.svc.create_order(VISITOR, 15)
        self.svc.approve(extra["code"])  # 4 credits total
        results = []
        threads = [threading.Thread(target=lambda: results.append(self.svc.revoke(order["code"])["removed"]))
                   for _ in range(10)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        self.assertEqual(sum(results), 3)
        self.assertEqual(self.svc.balance(VISITOR)["credits"], 1)

    def reopen(self):
        return billing.CreditService(billing.JsonStore(self.svc.store.dir))

    def test_balance_persists_after_restart(self):
        order = self.svc.create_order(VISITOR, 150)
        self.svc.approve(order["code"])
        self.svc.reserve_reading(OTHER)  # free question used
        pending = self.svc.create_order(OTHER, 45)
        reopened = self.reopen()
        self.assertEqual(reopened.balance(VISITOR)["credits"], 15)
        self.assertFalse(reopened.balance(OTHER)["freeAvailable"])
        self.assertEqual([o["code"] for o in reopened.list_orders("pending")], [pending["code"]])

    def test_same_price_pending_order_is_reused(self):
        a = self.svc.create_order(VISITOR, 60)
        b = self.svc.create_order(VISITOR, 60)
        self.assertEqual(a["code"], b["code"])
        for amount in (15, 30, 45, 75):
            self.svc.create_order(VISITOR, amount)
        with self.assertRaises(billing.PaymentError) as ctx:
            self.svc.create_order(VISITOR, 90)
        self.assertEqual(ctx.exception.status, 429)

    def test_release_gives_back(self):
        self.assertEqual(self.svc.reserve_reading(VISITOR), "free")
        self.svc.release_reading(VISITOR, "free")
        self.assertTrue(self.svc.balance(VISITOR)["freeAvailable"])
        self.svc.approve(self.svc.create_order(VISITOR, 15)["code"])
        self.svc.reserve_reading(VISITOR)  # paid
        self.svc.release_reading(VISITOR, "paid")
        self.assertEqual(self.svc.balance(VISITOR)["credits"], 1)

    def test_reject_then_cannot_approve(self):
        order = self.svc.create_order(VISITOR, 30)
        self.svc.reject(order["code"])
        with self.assertRaises(billing.PaymentError):
            self.svc.approve(order["code"])
        self.assertEqual(self.svc.balance(VISITOR)["credits"], 0)

    def test_concurrent_approve_adds_once(self):
        order = self.svc.create_order(VISITOR, 150)
        threads = [threading.Thread(target=self.svc.approve, args=(order["code"],)) for _ in range(20)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        self.assertEqual(self.svc.balance(VISITOR)["credits"], 15)

    def test_invalid_amount_rejected(self):
        with self.assertRaises(ValueError):
            self.svc.create_order(VISITOR, 100)

    def test_deduct_and_refuse(self):
        self.assertEqual(self.svc.reserve_reading(VISITOR), "free")
        with self.assertRaises(billing.PaymentError) as ctx:
            self.svc.reserve_reading(VISITOR)
        self.assertEqual(ctx.exception.status, 402)
        self.svc.approve(self.svc.create_order(VISITOR, 30)["code"])
        self.assertEqual(self.svc.reserve_reading(VISITOR), "paid")
        self.assertEqual(self.svc.balance(VISITOR)["credits"], 1)
        self.assertEqual(self.svc.reserve_reading(VISITOR), "paid")
        self.assertEqual(self.svc.balance(VISITOR)["credits"], 0)
        with self.assertRaises(billing.PaymentError):
            self.svc.reserve_reading(VISITOR)

    def test_concurrent_reserve_never_overdraws(self):
        self.svc.reserve_reading(VISITOR)  # use the free preview
        self.svc.approve(self.svc.create_order(VISITOR, 45)["code"])  # 3 credits
        wins = []

        def go():
            try:
                wins.append(self.svc.reserve_reading(VISITOR))
            except billing.PaymentError:
                pass

        threads = [threading.Thread(target=go) for _ in range(25)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        self.assertEqual(len(wins), 3)
        self.assertEqual(self.svc.balance(VISITOR)["credits"], 0)


class Http(unittest.TestCase):
    """End-to-end through the real HTTP handler with a mocked LLM."""

    @classmethod
    def setUpClass(cls):
        cls.env = mock.patch.dict(os.environ, {"PROMPTPAY_ID": "0812345678", "ADMIN_TOKEN": "test-secret-token"})
        cls.env.start()
        cls.server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.env.stop()

    make = staticmethod(json_service)

    def setUp(self):
        app.SERVICE = self.make()
        self.llm = mock.patch.object(app, "llm_generate", return_value=("AI reading text", {}))
        self.llm.start()
        self.sessions = {}  # visitor id -> session cookie (the visitor signed up)
        self.fast_hash = mock.patch.object(app.accounts, "PBKDF2_ITERATIONS", 2000)
        self.fast_hash.start()
        for lim in (app.accounts.LOGIN_BY_IP, app.accounts.LOGIN_BY_USER, app.accounts.SIGNUP_BY_IP,
                    app.accounts.SIGNUP_GLOBAL):
            lim._hits.clear()

    def tearDown(self):
        self.llm.stop()
        self.fast_hash.stop()

    def signup(self, visitor, username=None, password="moon-pass-123"):
        """Sign this visitor up (merging its balance); later requests carry the cookie."""
        username = username or ("u_" + visitor[:12])
        code, data, cookie = self.raw("POST", "/api/auth/signup", {"username": username, "password": password},
                                      {"X-Visitor-Id": visitor})
        assert code == 201, (code, data)
        self.sessions[visitor] = cookie
        return data

    def raw(self, method, path, body=None, headers=None):
        """Like req() but never adds cookies and also returns the Set-Cookie value."""
        data = json.dumps(body).encode() if body is not None else None
        r = urllib.request.Request(self.base + path, data=data, method=method, headers=headers or {})
        if data:
            r.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(r) as resp:
                ck = resp.headers.get("Set-Cookie")
                return resp.status, json.loads(resp.read() or b"{}"), ck
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}"), e.headers.get("Set-Cookie")

    def req(self, method, path, body=None, headers=None):
        headers = dict(headers or {})
        vid = headers.get("X-Visitor-Id")
        if vid and method == "POST" and path in ("/api/orders", "/api/reading") and vid not in self.sessions \
                and "Cookie" not in headers and not headers.pop("X-No-Auto-Login", None):
            self.signup(vid)  # asking and buying need an account: sign up first, like the UI asks
        if vid in self.sessions and "Cookie" not in headers:
            headers["Cookie"] = self.sessions[vid].split(";")[0]
        data = json.dumps(body).encode() if body is not None else None
        r = urllib.request.Request(self.base + path, data=data, method=method, headers=headers)
        if data:
            r.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(r) as resp:
                raw = resp.read()
                try:
                    return resp.status, json.loads(raw or b"{}")
                except ValueError:
                    return resp.status, {"raw": raw[:50]}
        except urllib.error.HTTPError as e:
            raw = e.read()
            try:
                return e.code, json.loads(raw)
            except ValueError:
                return e.code, {"raw": raw[:50]}

    def reading(self, visitor=VISITOR):
        return self.req("POST", "/api/reading",
                        {"name": "น้ำเพชร", "birthDate": "2006-07-07", "topic": "love", "lang": "th"},
                        {"X-Visitor-Id": visitor})

    ADMIN = {"X-Admin-Token": "test-secret-token"}

    def test_packages_endpoint(self):
        code, data = self.req("GET", "/api/packages")
        self.assertEqual(code, 200)
        self.assertTrue(data["paymentEnabled"])
        self.assertEqual({p["price"]: (p["questions"], p["bonus"], p["perQuestion"]) for p in data["packages"]}, EXPECTED)

    def test_full_flow(self):
        h = {"X-Visitor-Id": VISITOR}
        # Free preview first, then refusal at 0.
        code, data = self.reading()
        self.assertEqual(code, 200)
        self.assertEqual(data["charge"], {"kind": "free", "charged": True})
        self.assertFalse(data["premiumUnlocked"])
        code, data = self.reading()
        self.assertEqual(code, 402)
        self.assertEqual(data["code"], "no_credits")
        # Invalid amounts are rejected by the server.
        for bad in (100, 0, 165, "x", 15.5, None):
            code, _ = self.req("POST", "/api/orders", {"amount": bad}, h)
            self.assertEqual(code, 400, bad)
        # Order -> QR payload for that exact amount.
        code, data = self.req("POST", "/api/orders", {"amount": 90}, h)
        self.assertEqual(code, 200)
        order = data["order"]
        self.assertEqual((order["price"], order["questions"], order["bonus"]), (90, 7, 1))
        self.assertEqual(data["promptpay"]["payload"], billing.promptpay_payload("0812345678", 90))
        self.assertIn("540590.00", data["promptpay"]["payload"])
        # Admin auth.
        self.assertEqual(self.req("GET", "/api/admin/orders?status=pending")[0], 401)
        self.assertEqual(self.req("GET", "/api/admin/orders", headers={"X-Admin-Token": "wrong"})[0], 401)
        self.assertEqual(self.req("POST", f"/api/admin/orders/{order['code']}/approve")[0], 401)
        code, data = self.req("GET", "/api/admin/orders?status=pending", headers=self.ADMIN)
        self.assertEqual([o["code"] for o in data["orders"]], [order["code"]])
        # Approve -> balance, idempotent.
        code, data = self.req("POST", f"/api/admin/orders/{order['code']}/approve", headers=self.ADMIN)
        self.assertEqual((code, data["credits"], data["alreadyApproved"]), (200, 7, False))
        code, data = self.req("POST", f"/api/admin/orders/{order['code']}/approve", headers=self.ADMIN)
        self.assertEqual((code, data["credits"], data["alreadyApproved"]), (200, 7, True))
        self.assertEqual(self.req("GET", "/api/balance", headers=h)[1]["credits"], 7)
        # Each reading deducts exactly 1 and unlocks premium.
        code, data = self.reading()
        self.assertEqual((code, data["balance"]["credits"], data["premiumUnlocked"]), (200, 6, True))
        # Template fallback (AI down) does not charge.
        with mock.patch.object(app, "llm_generate", return_value=None):
            code, data = self.reading()
        self.assertEqual((code, data["charge"]["charged"], data["balance"]["credits"]), (200, False, 6))
        # Validation errors do not charge.
        code, _ = self.req("POST", "/api/reading", {"name": "", "birthDate": "2006-07-07"}, h)
        self.assertEqual(code, 400)
        self.assertEqual(self.req("GET", "/api/balance", headers=h)[1]["credits"], 6)
        # Other visitors are unaffected.
        self.assertEqual(self.req("GET", "/api/balance", headers={"X-Visitor-Id": OTHER})[1]["credits"], 0)

    def test_admin_reject_flow(self):
        h = {"X-Visitor-Id": VISITOR}
        code = self.req("POST", "/api/orders", {"amount": 15}, h)[1]["order"]["code"]
        self.assertEqual(self.req("POST", f"/api/admin/orders/{code}/reject")[0], 401)
        st, data = self.req("POST", f"/api/admin/orders/{code}/reject", headers=self.ADMIN)
        self.assertEqual((st, data["order"]["status"]), (200, "rejected"))
        self.assertIsNotNone(data["order"]["decidedAt"])
        # Rejecting twice is harmless; it is gone from pending and cannot be approved.
        self.assertEqual(self.req("POST", f"/api/admin/orders/{code}/reject", headers=self.ADMIN)[0], 200)
        pending = self.req("GET", "/api/admin/orders?status=pending", headers=self.ADMIN)[1]["orders"]
        self.assertNotIn(code, [o["code"] for o in pending])
        st, data = self.req("POST", f"/api/admin/orders/{code}/approve", headers=self.ADMIN)
        self.assertEqual((st, data["code"]), (409, "not_pending"))
        self.assertEqual(self.req("GET", "/api/balance", headers=h)[1]["credits"], 0)
        # Lower-case codes work; unknown codes give a clear 404.
        code2 = self.req("POST", "/api/orders", {"amount": 30}, h)[1]["order"]["code"]
        self.assertEqual(self.req("POST", f"/api/admin/orders/{code2.lower()}/reject", headers=self.ADMIN)[0], 200)
        st, data = self.req("POST", "/api/admin/orders/MZZZZZ/reject", headers=self.ADMIN)
        self.assertEqual((st, data["code"]), (404, "not_found"))
        # Approved orders cannot be rejected.
        code3 = self.req("POST", "/api/orders", {"amount": 45}, h)[1]["order"]["code"]
        self.req("POST", f"/api/admin/orders/{code3}/approve", headers=self.ADMIN)
        self.assertEqual(self.req("POST", f"/api/admin/orders/{code3}/reject", headers=self.ADMIN)[0], 409)

    def test_admin_revoke_flow(self):
        h = {"X-Visitor-Id": VISITOR}
        code = self.req("POST", "/api/orders", {"amount": 45}, h)[1]["order"]["code"]
        # Admin token required.
        self.assertEqual(self.req("POST", f"/api/admin/orders/{code}/revoke")[0], 401)
        self.assertEqual(self.req("POST", f"/api/admin/orders/{code}/revoke", headers={"X-Admin-Token": "wrong"})[0], 401)
        # Pending orders can't be revoked.
        st, data = self.req("POST", f"/api/admin/orders/{code}/revoke", headers=self.ADMIN)
        self.assertEqual((st, data["code"]), (409, "not_approved"))
        self.req("POST", f"/api/admin/orders/{code}/approve", headers=self.ADMIN)
        self.assertEqual(self.req("GET", "/api/balance", headers=h)[1]["credits"], 3)
        self.reading()  # customer used one
        out = io.StringIO()
        with mock.patch("sys.stdout", out):
            st, data = self.req("POST", f"/api/admin/orders/{code}/revoke", headers=self.ADMIN)
        self.assertEqual((st, data["removed"], data["credits"], data["order"]["status"]), (200, 2, 0, "rejected"))
        self.assertIn(f"Admin revoked order {code}: took back 2 of 3", out.getvalue())
        self.assertNotIn(self.ADMIN["X-Admin-Token"], out.getvalue())
        self.assertNotIn(VISITOR, out.getvalue())
        self.assertEqual(self.req("GET", "/api/balance", headers=h)[1]["credits"], 0)
        st, data = self.req("POST", f"/api/admin/orders/{code}/revoke", headers=self.ADMIN)
        self.assertEqual((st, data["alreadyRevoked"], data["removed"]), (200, True, 0))
        approved = self.req("GET", "/api/admin/orders?status=approved", headers=self.ADMIN)[1]["orders"]
        self.assertNotIn(code, [o["code"] for o in approved])
        st, data = self.req("POST", f"/api/admin/orders/{code}/approve", headers=self.ADMIN)
        self.assertEqual((st, data["code"]), (409, "not_pending"))
        # The customer sees it as rejected.
        mine = self.req("GET", "/api/orders", headers=h)[1]["orders"]
        self.assertEqual({o["code"]: o["status"] for o in mine}[code], "rejected")

    def test_admin_page_has_two_tap_revoke(self):
        html = (ROOT / "static" / "admin.html").read_text(encoding="utf-8")
        self.assertIn("ดึงเครดิตคืน", html)
        self.assertIn('data-act="revoke"', html)
        self.assertIn("แตะอีกครั้งเพื่อดึงคืน", html)
        self.assertIn("อนุมัติวันนี้", html)

    def test_admin_page_does_not_rely_on_native_dialogs(self):
        import re
        html = (ROOT / "static" / "admin.html").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"\b(confirm|alert|prompt)\s*\(", html))

    def test_reading_requires_login(self):
        code, data = self.req("POST", "/api/reading", {"name": "x", "birthDate": "2006-07-07"})
        self.assertEqual((code, data["code"]), (401, "login_required"))
        code, data = self.req("POST", "/api/reading", {"name": "x"},
                              {"X-Visitor-Id": VISITOR, "X-No-Auto-Login": "1"})
        self.assertEqual((code, data["code"]), (401, "login_required"))
        self.assertIn("สมัคร", data["error"])

    def test_admin_page_401_without_token(self):
        code, _ = self.req("GET", "/admin")
        self.assertEqual(code, 401)
        code, _ = self.req("GET", "/admin", headers=self.ADMIN)
        self.assertEqual(code, 200)

    def test_payment_disabled_without_promptpay(self):
        with mock.patch.dict(os.environ, {"PROMPTPAY_ID": ""}):
            self.assertFalse(self.req("GET", "/api/packages")[1]["paymentEnabled"])
            code, data = self.req("POST", "/api/orders", {"amount": 15}, {"X-Visitor-Id": VISITOR})
            self.assertEqual((code, data["code"]), (503, "payment_disabled"))

    def test_admin_disabled_without_token_env(self):
        with mock.patch.dict(os.environ, {"ADMIN_TOKEN": ""}):
            self.assertEqual(self.req("GET", "/api/admin/orders", headers={"X-Admin-Token": ""})[0], 503)
            self.assertEqual(self.req("GET", "/admin")[0], 401)


def go_free(svc, visitor, wins):
    try:
        wins.append(svc.reserve_reading(visitor))
    except billing.PaymentError:
        pass


@unittest.skipUnless(TEST_PG, "set TEST_DATABASE_URL to run against Postgres")
class PgOrders(Orders):
    make = staticmethod(pg_service)

    def reopen(self):
        # A brand-new connection/service, like a restarted server.
        return billing.PostgresCreditService(TEST_PG)

    def test_races_across_separate_connections(self):
        services = [billing.PostgresCreditService(TEST_PG) for _ in range(4)]
        self.svc.reserve_reading(VISITOR)  # free preview
        order = self.svc.create_order(VISITOR, 45)  # 3 questions
        threads = [threading.Thread(target=services[i % 4].approve, args=(order["code"],)) for i in range(12)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        self.assertEqual(self.svc.balance(VISITOR)["credits"], 3)
        wins = []

        def go(svc):
            try:
                wins.append(svc.reserve_reading(VISITOR))
            except billing.PaymentError:
                pass

        threads = [threading.Thread(target=go, args=(services[i % 4],)) for i in range(20)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        self.assertEqual(wins, ["paid"] * 3)
        self.assertEqual(self.svc.balance(VISITOR)["credits"], 0)
        new_visitor = "d" * 32
        threads = [threading.Thread(target=go_free, args=(services[i % 4], new_visitor, wins)) for i in range(10)]
        wins.clear()
        [t.start() for t in threads]
        [t.join() for t in threads]
        self.assertEqual(wins, ["free"])  # only one free question, even under races
        for svc in services:
            svc.close()


@unittest.skipUnless(TEST_PG, "set TEST_DATABASE_URL to run against Postgres")
class PgHttp(Http):
    make = staticmethod(pg_service)


class DatabaseUrl(unittest.TestCase):
    def test_parse_and_default_ssl(self):
        cfg = billing.parse_database_url("postgresql://u:p%40ss@ep-x.aws.neon.tech/neondb")
        self.assertEqual((cfg["host"], cfg["port"], cfg["user"], cfg["password"], cfg["database"], cfg["sslmode"]),
                         ("ep-x.aws.neon.tech", 5432, "u", "p@ss", "neondb", "require"))

    def test_copy_paste_wrappers_are_forgiven(self):
        good = "postgresql://u:pw@ep-x.neon.tech/neondb?sslmode=require&channel_binding=require"
        for wrapped in (f"psql '{good}'", f'"{good}"', f"DATABASE_URL={good}", f"  {good}\n", f"psql \"{good}\"", f"Connection string: {good}", f"psql -d {good} --x", f"export X='{good}'"):
            self.assertEqual(billing.parse_database_url(wrapped)["host"], "ep-x.neon.tech", wrapped)

    def test_bad_urls_do_not_leak(self):
        for bad in ("mysql://u:secretpw@h/db", "postgresql://u:secretpw@/db", "postgresql://u:secretpw@h:abc/db",
                    "postgresql://u:secretpw@h/db?sslmode=bogus", "neondb", "jdbc:postgresql://h/db?password=secretpw",
                    "host=h password=secretpw", "label postgresql://u:secretpw@/db"):
            with self.assertRaises(billing.DatabaseConfigError) as ctx:
                billing.parse_database_url(bad)
            self.assertNotIn("secretpw", str(ctx.exception))

    @unittest.skipUnless(TEST_PG, "needs Postgres")
    def test_wrong_and_masked_password_hints(self):
        from urllib.parse import urlsplit
        parts = urlsplit(TEST_PG)
        host = f"{parts.hostname}:{parts.port}"
        for pw, hint in (("********", "looks masked"), ("definitely-wrong", "does not match")):
            with self.assertRaises(billing.DatabaseConfigError) as ctx:
                billing.PostgresCreditService(f"postgresql://moonuser:{pw}@{host}/moontest?sslmode=disable")
            self.assertIn(hint, str(ctx.exception))
            self.assertNotIn(pw, str(ctx.exception))

    def test_low_scram_iteration_servers_are_accepted(self):
        billing._import_pg8000()
        import scramp.core
        self.assertEqual(scramp.core.IterationCount(1024).value, 1024)

    def test_connection_failure_falls_back_to_json(self):
        url = "postgresql://u:secretpw@127.0.0.1:1/db?sslmode=disable"
        with mock.patch.dict(os.environ, {"DATABASE_URL": url}):
            svc, kind, problem = billing.make_service(tempfile.mkdtemp())
        self.assertEqual(kind, "json")
        self.assertIn("Could not connect", problem)
        self.assertNotIn("secretpw", problem)


if __name__ == "__main__":
    unittest.main()
