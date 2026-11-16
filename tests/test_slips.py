"""Slip upload + SlipOK verification (SlipOK is always mocked here).

Run: python3 -m unittest discover -s tests -v
"""

import os
import socket
import sys
import urllib.error
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app  # noqa: E402
import slips  # noqa: E402
import test_credits as tc  # noqa: E402

TEST_PG, VISITOR, OTHER, pg_service = tc.TEST_PG, tc.VISITOR, tc.OTHER, tc.pg_service

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
JPG = b"\xff\xd8\xff\xe0" + b"\x00" * 64
WEBP = b"RIFF\x00\x00\x00\x00WEBPVP8 " + b"\x00" * 64
SLIP_ENV = {"SLIPOK_BRANCH_ID": "12345", "SLIPOK_API_KEY": "test-slipok-key"}


def ok_payload(ref="REF001", amount=15):
    return {"success": True, "data": {
        "success": True, "transRef": ref, "amount": amount, "transDate": "20261116", "transTime": "12:00:00",
        "sender": {"displayName": "นาย ทดสอบ"}, "receiver": {"displayName": "น.ส. ถามจันทร์"},
        "sendingBank": "004", "receivingBank": "014"}}


def err_payload(code, data=None):
    return {"code": code, "message": f"error {code}", "data": data}


class SlipHttp(tc.Http):
    """POST /api/orders/<code>/slip end to end with SlipOK mocked."""

    def setUp(self):
        super().setUp()
        self.env2 = mock.patch.dict(os.environ, SLIP_ENV)
        self.env2.start()
        slips.LIMITER = slips.VisitorLimiter()
        self.sleep = mock.patch.object(slips.time, "sleep")
        self.sleep.start()
        self.calls = []

    def tearDown(self):
        self.sleep.stop()
        self.env2.stop()
        super().tearDown()

    def mock_slipok(self, *responses):
        """Each response is (status, payload) or an exception to raise."""
        seq = list(responses)

        def fake(image, mime, amount):
            self.calls.append((mime, amount))
            r = seq.pop(0) if len(seq) > 1 else seq[0]
            if isinstance(r, BaseException):
                raise r
            return r
        return mock.patch.object(slips, "slipok_request", side_effect=fake)

    def order(self, price=15, visitor=VISITOR):
        code, data = self.req("POST", "/api/orders", {"amount": price}, {"X-Visitor-Id": visitor})
        self.assertEqual(code, 200, data)
        return data["order"]["code"]

    def upload(self, code, body=PNG, visitor=VISITOR, ctype="image/png"):
        import json as _json
        import urllib.request as ur
        r = ur.Request(f"{self.base}/api/orders/{code}/slip", data=body, method="POST",
                       headers={"X-Visitor-Id": visitor, "Content-Type": ctype})
        try:
            with ur.urlopen(r) as resp:
                return resp.status, _json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return e.code, _json.loads(e.read() or b"{}")

    def admin_order(self, code):
        _, data = self.req("GET", "/api/admin/orders", headers=self.ADMIN)
        return next(o for o in data["orders"] if o["code"] == code)

    def credits(self, visitor=VISITOR):
        _, data = self.req("GET", "/api/balance", headers={"X-Visitor-Id": visitor})
        return data["credits"]

    # -- tests ----------------------------------------------------------------
    def test_enabled_flag_and_disabled_hides(self):
        _, data = self.req("GET", "/api/packages")
        self.assertTrue(data["slipEnabled"])
        with mock.patch.dict(os.environ, {"SLIPOK_API_KEY": ""}):
            _, data = self.req("GET", "/api/packages")
            self.assertFalse(data["slipEnabled"])
            self.assertTrue(data["paymentEnabled"])  # QR flow unchanged
            code = self.order()
            status, body = self.upload(code)
            self.assertEqual((status, body.get("code")), (503, "slip_disabled"))

    def test_success_approves_and_adds_credits(self):
        code = self.order(90)
        with self.mock_slipok((200, ok_payload("REF-OK", 90))):
            status, data = self.upload(code, JPG, ctype="image/jpeg")
        self.assertEqual(status, 200, data)
        self.assertEqual(data["result"], "success")
        self.assertEqual(data["order"]["status"], "approved")
        self.assertEqual(data["balance"]["credits"], 7)
        self.assertEqual(self.calls, [("image/jpeg", 90)])
        o = self.admin_order(code)
        self.assertEqual(o["slipStatus"], "verified")
        self.assertEqual(o["slipTransRef"], "REF-OK")
        self.assertEqual(o["slipSummary"]["sender"], "นาย ทดสอบ")
        # Uploading again after approval doesn't call SlipOK or add credits twice.
        with self.mock_slipok((200, ok_payload("REF-OK", 90))):
            status, data = self.upload(code)
        self.assertEqual((status, data["result"], data["balance"]["credits"]), (200, "success", 7))
        self.assertEqual(len(self.calls), 1)
        # Admin approve afterwards is idempotent.
        status, data = self.req("POST", f"/api/admin/orders/{code}/approve", {}, self.ADMIN)
        self.assertEqual(status, 200)
        self.assertEqual(self.credits(), 7)

    def test_webp_accepted(self):
        code = self.order()
        with self.mock_slipok((200, ok_payload("REF-W"))):
            status, data = self.upload(code, WEBP, ctype="image/webp")
        self.assertEqual((status, data["result"]), (200, "success"))

    def test_duplicate_trans_ref_across_orders(self):
        a = self.order(15)
        with self.mock_slipok((200, ok_payload("REF-DUP"))):
            self.assertEqual(self.upload(a)[1]["result"], "success")
        b = self.order(15, OTHER)
        with self.mock_slipok((200, ok_payload("REF-DUP"))):
            status, data = self.upload(b, visitor=OTHER)
        self.assertEqual((status, data["result"], data["code"]), (200, "failed", "duplicate_local"))
        self.assertEqual(data["order"]["status"], "pending")
        self.assertEqual(self.credits(OTHER), 0)
        self.assertIn("ใช้ไปแล้ว", data["messageTh"])
        self.assertEqual(self.admin_order(b)["slipStatus"], "failed")

    def test_clear_failures_keep_pending(self):
        cases = {
            1012: ("failed", "duplicate"), 1013: ("failed", "amount"), 1014: ("failed", "receiver"),
            1005: ("failed", "not_slip"), 1006: ("failed", "not_slip"), 1007: ("failed", "not_slip"),
            1008: ("failed", "not_slip"),
        }
        for err, (kind, msg) in cases.items():
            with self.subTest(code=err):
                slips.LIMITER = slips.VisitorLimiter()
                code = self.order(15)
                with self.mock_slipok((400, err_payload(err, {"amount": 30}))):
                    status, data = self.upload(code)
                self.assertEqual((status, data["result"], data["code"]), (200, kind, str(err)))
                self.assertEqual(data["messageTh"], slips.MSG[msg][0])
                self.assertEqual(data["messageEn"], slips.MSG[msg][1])
                self.assertEqual(data["order"]["status"], "pending")
                self.assertEqual(self.credits(), 0)
                self.req("POST", f"/api/admin/orders/{code}/reject", {}, self.ADMIN)

    def test_uncertain_goes_to_review(self):
        for err in (1000, 1001, 1002, 1003, 1004, 1009, 1010, 1011, 1099):
            with self.subTest(code=err):
                slips.LIMITER = slips.VisitorLimiter()
                code = self.order(15)
                data_field = {"delay": 5} if err == 1010 else None
                with self.mock_slipok((400, err_payload(err, data_field))):
                    status, data = self.upload(code)
                self.assertEqual((status, data["result"]), (200, "review"))
                self.assertEqual(data["order"]["status"], "pending")
                self.assertEqual(data["order"]["slipStatus"], "review")
                o = self.admin_order(code)
                self.assertEqual(o["slipStatus"], "review")
                self.assertIn(str(err), o["slipNote"])
                if err == 1010:
                    self.assertEqual(data["messageEn"], slips.MSG["delay"][1])
                self.req("POST", f"/api/admin/orders/{code}/reject", {}, self.ADMIN)

    def test_timeout_retries_once_then_review(self):
        code = self.order()
        with self.mock_slipok(TimeoutError("timed out")):
            status, data = self.upload(code)
        self.assertEqual(len(self.calls), 2)
        self.assertEqual((status, data["result"], data["code"]), (200, "review", "timeout"))
        self.assertIn("timeout", self.admin_order(code)["slipNote"])
        self.assertEqual(self.credits(), 0)

    def test_timeout_then_success_on_retry(self):
        code = self.order()
        with self.mock_slipok(urllib.error.URLError(socket.timeout("timed out")), (200, ok_payload("REF-R"))):
            status, data = self.upload(code)
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(data["result"], "success")
        self.assertEqual(self.credits(), 1)

    def test_5xx_retry_and_1012_after_retry_is_review(self):
        code = self.order()
        with self.mock_slipok((502, {}), (400, err_payload(1012, {"amount": 15, "transRef": "X"}))):
            status, data = self.upload(code)
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(data["result"], "review")

    def test_local_amount_mismatch_on_success(self):
        code = self.order(30)
        with self.mock_slipok((200, ok_payload("REF-AMT", 15))):
            status, data = self.upload(code)
        self.assertEqual((data["result"], data["code"]), ("failed", "amount_local"))
        self.assertEqual(self.credits(), 0)
        self.assertIsNone(self.admin_order(code).get("slipTransRef"))

    def test_wrong_file_type_and_size(self):
        code = self.order()
        with self.mock_slipok((200, ok_payload())):
            status, data = self.upload(code, b"%PDF-1.4 not an image", ctype="image/png")
            self.assertEqual((status, data["code"]), (415, "bad_file_type"))
            status, data = self.upload(code, b"GIF89a" + b"\x00" * 20, ctype="image/gif")
            self.assertEqual(status, 415)
            status, data = self.upload(code, b"", ctype="image/png")
            self.assertEqual(status, 400)
            big = PNG + b"\x00" * (slips.MAX_BYTES + 1)
            try:
                status, data = self.upload(code, big)
                self.assertEqual((status, data["code"]), (413, "file_too_large"))
            except (ConnectionError, urllib.error.URLError):
                pass  # server may close before the client finishes sending; still rejected
        self.assertEqual(self.calls, [])

    def test_other_visitor_cannot_use_order(self):
        code = self.order()
        with self.mock_slipok((200, ok_payload("REF-X"))):
            status, data = self.upload(code, visitor=OTHER)
        self.assertEqual((status, data["code"]), (404, "not_found"))
        self.assertEqual(self.calls, [])

    def test_rejected_order_closed(self):
        code = self.order()
        self.req("POST", f"/api/admin/orders/{code}/reject", {}, self.ADMIN)
        with self.mock_slipok((200, ok_payload("REF-C"))):
            status, data = self.upload(code)
        self.assertEqual((status, data["code"]), (409, "not_pending"))
        self.assertEqual(self.calls, [])

    def test_rate_limits(self):
        code = self.order()
        with self.mock_slipok((400, err_payload(1007))):
            for _ in range(slips.MAX_ATTEMPTS_PER_ORDER):
                self.assertEqual(self.upload(code)[0], 200)
            status, data = self.upload(code)
            self.assertEqual((status, data["code"]), (429, "too_many_slips"))
            # Per-visitor window across orders.
            slips.LIMITER = slips.VisitorLimiter(limit=2, window=600)
            other = self.order(30)
            self.assertEqual(self.upload(other)[0], 200)
            self.assertEqual(self.upload(other)[0], 200)
            status, data = self.upload(other)
            self.assertEqual((status, data["code"]), (429, "rate_limited"))

    def test_secrets_not_in_responses(self):
        code = self.order()
        with self.mock_slipok((400, err_payload(1002))):
            status, data = self.upload(code)
        self.assertNotIn("test-slipok-key", repr(data))
        _, adm = self.req("GET", "/api/admin/orders", headers=self.ADMIN)
        self.assertNotIn("test-slipok-key", repr(adm))
        _, health = self.req("GET", "/api/health")
        self.assertNotIn("test-slipok-key", repr(health))


@unittest.skipUnless(TEST_PG, "set TEST_DATABASE_URL to run against Postgres")
class PgSlipHttp(SlipHttp):
    make = staticmethod(pg_service)


class SlipOKRequest(unittest.TestCase):
    """The real request builder, with urlopen mocked (no network)."""

    def test_request_shape(self):
        seen = {}

        class Resp:
            status = 200
            def read(self):
                return b'{"success": true, "data": {"transRef": "R"}}'
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False

        def fake_urlopen(req, timeout):
            seen.update(url=req.full_url, headers=dict(req.header_items()), body=req.data, timeout=timeout)
            return Resp()

        with mock.patch.dict(os.environ, SLIP_ENV), mock.patch.object(slips.urllib.request, "urlopen", fake_urlopen):
            status, payload = slips.slipok_request(PNG, "image/png", 45)
        self.assertEqual(status, 200)
        self.assertTrue(seen["url"].endswith("/api/line/apikey/12345"))
        self.assertEqual(seen["headers"].get("X-authorization"), "test-slipok-key")
        body = seen["body"]
        self.assertIn(b'name="amount"\r\n\r\n45\r\n', body)
        self.assertIn(b'name="log"\r\n\r\ntrue\r\n', body)
        self.assertIn(b'name="files"; filename="slip.png"', body)
        self.assertIn(PNG, body)
        self.assertEqual(seen["timeout"], slips.TIMEOUT_SECONDS)

    def test_sniff(self):
        self.assertEqual(slips.sniff_image(JPG), "image/jpeg")
        self.assertEqual(slips.sniff_image(PNG), "image/png")
        self.assertEqual(slips.sniff_image(WEBP), "image/webp")
        self.assertIsNone(slips.sniff_image(b"GIF89a"))


if __name__ == "__main__":
    unittest.main()
