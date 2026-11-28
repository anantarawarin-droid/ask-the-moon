"""Slip upload + SlipOK verification (SlipOK is always mocked here).

Run: python3 -m unittest discover -s tests -v
"""

import json
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

        def fake(image, mime, amount=None, qr=None, log=True, qr_form=False):
            call = (mime, amount) if qr is None else (mime, amount, qr)
            if qr_form:
                call += ("form",)
            if not log:
                call += ("nolog",)
            self.calls.append(call)
            r = seq.pop(0) if len(seq) > 1 else seq[0]
            if isinstance(r, BaseException):
                raise r
            return r
        return mock.patch.object(slips, "slipok_request", side_effect=fake)

    def order(self, price=15, visitor=VISITOR):
        code, data = self.req("POST", "/api/orders", {"amount": price}, {"X-Visitor-Id": visitor})
        self.assertEqual(code, 200, data)
        return data["order"]["code"]

    def upload(self, code, body=PNG, visitor=VISITOR, ctype="image/png", qr=None):
        import json as _json
        import urllib.request as ur
        headers = {"X-Visitor-Id": visitor, "Content-Type": ctype}
        if qr:
            headers["X-Slip-QR"] = qr
        if visitor in self.sessions:
            headers["Cookie"] = self.sessions[visitor].split(";")[0]
        r = ur.Request(f"{self.base}/api/orders/{code}/slip", data=body, method="POST", headers=headers)
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
        q90 = tc.questions_of(90)
        self.assertEqual(data["balance"]["credits"], q90)
        self.assertEqual(self.calls, [("image/jpeg", None)])  # amount is checked locally, not sent
        o = self.admin_order(code)
        self.assertEqual(o["slipStatus"], "verified")
        self.assertEqual(o["slipTransRef"], "REF-OK")
        self.assertEqual(o["slipSummary"]["sender"], "นาย ทดสอบ")
        # Uploading again after approval doesn't call SlipOK or add credits twice.
        with self.mock_slipok((200, ok_payload("REF-OK", 90))):
            status, data = self.upload(code)
        self.assertEqual((status, data["result"], data["balance"]["credits"]), (200, "success", q90))
        self.assertEqual(len(self.calls), 1)
        # Admin approve afterwards is idempotent.
        status, data = self.req("POST", f"/api/admin/orders/{code}/approve", {}, self.ADMIN)
        self.assertEqual(status, 200)
        self.assertEqual(self.credits(), q90)

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
            1008: ("failed", "not_slip"), 1000: ("failed", "not_slip"),
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
        for err in (1001, 1002, 1003, 1004, 1009, 1010, 1011, 1099):
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

    def test_rejected_order_still_takes_a_late_slip(self):
        code = self.order()
        self.req("POST", f"/api/admin/orders/{code}/reject", {}, self.ADMIN)
        with self.mock_slipok((200, ok_payload("REF-C"))):
            status, data = self.upload(code)
        self.assertEqual((status, data["result"], data["order"]["status"]), (200, "success", "approved"))
        self.assertEqual(self.credits(), 1)

    def test_rate_limits(self):
        code = self.order()
        with self.mock_slipok((400, err_payload(1013, {"amount": 30}))):
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

    def test_unreadable_and_setup_problems_do_not_use_attempts(self):
        code = self.order()
        slips.LIMITER = slips.VisitorLimiter(limit=100, window=600)
        for err in (1000, 1007, 1006, 1003, 1004, 1000, 1000):
            with self.mock_slipok((400, err_payload(err))):
                self.assertEqual(self.upload(code)[0], 200)
        with self.mock_slipok(TimeoutError("timed out")):
            self.assertEqual(self.upload(code)[0], 200)
        self.assertEqual(self.admin_order(code)["slipAttempts"], 0)
        # The customer can still upload the right slip afterwards.
        with self.mock_slipok((200, ok_payload("REF-LATE"))):
            status, data = self.upload(code)
        self.assertEqual(data["result"], "success")

    def test_1000_message_asks_for_full_clear_slip(self):
        code = self.order()
        with self.mock_slipok((400, err_payload(1000))):
            _, data = self.upload(code)
        self.assertEqual((data["result"], data["code"]), ("failed", "1000"))
        self.assertIn("เต็มใบ", data["messageTh"])
        self.assertIn("QR", data["messageEn"])
        self.assertIn("doesn't count", data["messageEn"])
        self.assertIn("1000", self.admin_order(code)["slipNote"])

    def test_browser_qr_used_when_slipok_cannot_read_the_image(self):
        qr = "0041000600000101030040220013071152533APM077365102TH91048134"
        code = self.order()
        with self.mock_slipok((400, err_payload(1000)), (200, ok_payload("REF-QR"))):
            status, data = self.upload(code, qr=qr)
        self.assertEqual(data["result"], "success")
        self.assertEqual(self.calls, [("image/png", None), ("image/png", None, qr)])
        # No QR from the browser: no second call.
        self.calls.clear()
        other = self.order(30)
        with self.mock_slipok((400, err_payload(1000)), (200, ok_payload("REF-QR2", 30))):
            _, data = self.upload(other)
        self.assertEqual((data["result"], len(self.calls)), ("failed", 1))
        # A readable image is never re-checked with the QR text.
        self.calls.clear()
        third = self.order(45)
        with self.mock_slipok((400, err_payload(1013, {"amount": 30}))):
            _, data = self.upload(third, qr=qr)
        self.assertEqual(len(self.calls), 1)

    def test_422_1000_is_a_setup_problem_not_the_customers_slip(self):
        """Live 17 Nov: SlipOK answered HTTP 422 code 1000 to the image and to the QR text."""
        qr = "0041000600000101030040220013071152533APM077365102TH91048134"
        code = self.order()
        rej = (422, {"code": 1000, "message": "กรุณาใส่ข้อมูลให้ถูกต้อง"})
        with self.mock_slipok(rej):
            _, data = self.upload(code, qr=qr)
        self.assertEqual(self.calls, [("image/png", None), ("image/png", None, qr)])
        self.assertEqual((data["result"], data["code"]), ("review", "1000-422"))
        self.assertIn("ไม่ต้องอัปโหลดซ้ำ", data["messageTh"])
        order = self.admin_order(code)
        self.assertEqual((order["status"], order["slipStatus"], order["slipAttempts"]), ("pending", "review", 0))
        self.assertIn("setup", order["slipNote"])
        # Once SlipOK works again the same order still auto-approves.
        self.calls.clear()
        with self.mock_slipok((200, ok_payload("REF-AFTER"))):
            _, data = self.upload(code, qr=qr)
        self.assertEqual(data["result"], "success")

    def test_422_for_bad_branch_id_stops_after_one_call_and_names_the_setting(self):
        """SlipOK's real answer when the URL's branch id isn't a number (reproduced 17 Nov)."""
        qr = "0041000600000101030040220013071152533APM077365102TH91048134"
        code = self.order()
        rej = (422, {"code": 1000, "message": "กรุณาใส่ข้อมูลให้ถูกต้อง", "statusCode": 422,
                     "errors": [{"value": "x", "msg": "กรุณาใส่ข้อมูลให้ถูกต้อง", "param": "id", "location": "params"}]})
        with self.mock_slipok(rej):
            _, data = self.upload(code, qr=qr)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual((data["result"], data["code"]), ("review", "1000-422"))
        self.assertIn("SLIPOK_BRANCH_ID", self.admin_order(code)["slipNote"])

    def test_branch_id_copy_paste_variants(self):
        for raw in ("12345", " 12345\n", "'12345'", '"12345"', "12 345", "Branch ID: 12345", "\ufeff12345\u200b",
                    "https://api.slipok.com/api/line/apikey/12345", "<12345>"):
            self.assertEqual(slips.normalize_branch(raw), "12345", raw)
        self.assertFalse(slips.normalize_branch("abc").isdigit())
        with mock.patch.dict(os.environ, {"SLIPOK_BRANCH_ID": " 'Branch: 12345' ", "SLIPOK_API_KEY": " k "}):
            self.assertEqual(slips.config(), ("12345", "k"))
            self.assertIsNone(slips.config_problem())
        # Swapped by mistake: the numeric value is used as the branch.
        with mock.patch.dict(os.environ, {"SLIPOK_BRANCH_ID": "SLIPOKABCDEF", "SLIPOK_API_KEY": "12345"}):
            self.assertEqual(slips.config(), ("12345", "SLIPOKABCDEF"))
        with mock.patch.dict(os.environ, {"SLIPOK_BRANCH_ID": "SLIPOKABCDEF", "SLIPOK_API_KEY": "SLIPOKXYZ"}):
            note = slips.config_problem()
            self.assertIn("not a number", note)
            self.assertNotIn("SLIPOKABCDEF", note)
            self.assertNotIn("SLIPOKXYZ", note)

    def test_request_url_uses_clean_numeric_branch(self):
        seen = {}

        class Resp:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def read(self): return b'{"success": true}'

        def fake(req, timeout=None):
            seen["url"] = req.full_url
            return Resp()
        with mock.patch.dict(os.environ, {"SLIPOK_BRANCH_ID": "12345\r\n", "SLIPOK_API_KEY": "k"}), \
                mock.patch.object(slips.urllib.request, "urlopen", fake):
            slips.slipok_request(PNG, "image/png")
        self.assertEqual(seen["url"], "https://api.slipok.com/api/line/apikey/12345")

    def test_bad_qr_header_ignored(self):
        self.assertIsNone(slips.clean_qr("short"))
        self.assertIsNone(slips.clean_qr("ข้อความไทยที่ยาวพอสมควรแต่ไม่ใช่ ascii"))
        self.assertIsNone(slips.clean_qr("A" * 600))
        self.assertEqual(slips.clean_qr("0041000600000101%2003"), "0041000600000101 03")

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
            status, payload = slips.slipok_request(PNG, "image/png")
        self.assertEqual(status, 200)
        self.assertTrue(seen["url"].endswith("/api/line/apikey/12345"))
        self.assertEqual(seen["headers"].get("X-authorization"), "test-slipok-key")
        self.assertNotIn("Python-urllib", seen["headers"].get("User-agent", ""))  # Cloudflare blocks it
        self.assertTrue(seen["headers"].get("User-agent"))
        body = seen["body"]
        self.assertNotIn(b'name="amount"', body)  # checked locally
        self.assertIn(b'name="log"\r\n\r\ntrue\r\n', body)
        self.assertIn(b'name="files"; filename="slip.png"', body)
        self.assertIn(PNG, body)
        self.assertEqual(seen["timeout"], slips.TIMEOUT_SECONDS)
        # With the QR text from the browser: SlipOK's JSON "data" field, no image.
        with mock.patch.dict(os.environ, SLIP_ENV), mock.patch.object(slips.urllib.request, "urlopen", fake_urlopen):
            slips.slipok_request(PNG, "image/png", 45, qr="00410006ABC")
        self.assertEqual(json.loads(seen["body"]), {"data": "00410006ABC", "amount": 45, "log": True})
        self.assertEqual(seen["headers"].get("Content-type"), "application/json")
        with mock.patch.dict(os.environ, SLIP_ENV), mock.patch.object(slips.urllib.request, "urlopen", fake_urlopen):
            slips.slipok_request(PNG, "image/png", None, qr="00410006ABC", qr_form=True)
        self.assertIn(b'name="data"\r\n\r\n00410006ABC\r\n', seen["body"])
        self.assertIn(b'name="log"\r\n\r\ntrue\r\n', seen["body"])
        self.assertNotIn(b'name="files"', seen["body"])
        self.assertTrue(seen["headers"].get("Content-type").startswith("multipart/form-data"))
        with mock.patch.dict(os.environ, SLIP_ENV), mock.patch.object(slips.urllib.request, "urlopen", fake_urlopen):
            slips.slipok_request(PNG, "image/png", None, log=False)
        self.assertNotIn(b'name="log"', seen["body"])
        self.assertIn(b'name="files"', seen["body"])

    def test_sniff(self):
        self.assertEqual(slips.sniff_image(JPG), "image/jpeg")
        self.assertEqual(slips.sniff_image(PNG), "image/png")
        self.assertEqual(slips.sniff_image(WEBP), "image/webp")
        self.assertIsNone(slips.sniff_image(b"GIF89a"))


if __name__ == "__main__":
    unittest.main()


class BrowserQr(unittest.TestCase):
    def test_client_reads_qr_and_sends_it(self):
        static = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")
        with open(os.path.join(static, "app.js"), encoding="utf-8") as fh:
            js = fh.read()
        self.assertIn('headers["X-Slip-QR"] = encodeURIComponent(prepared.qr)', js)
        self.assertIn('s.src = "/vendor/jsQR.js?v=bc40c8a151"', js)
        self.assertTrue(os.path.exists(os.path.join(static, "vendor", "jsQR.js")))


class AdminPage(unittest.TestCase):
    """Static checks on the admin page's slip labels and the no-slip approve guard."""

    def setUp(self):
        self.html = (Path(__file__).resolve().parent.parent / "static" / "admin.html").read_text("utf-8")

    def test_waiting_for_slip_label(self):
        self.assertIn("⏳ รอลูกค้าอัปโหลดสลิป · สร้างเมื่อ", self.html)
        self.assertIn("นาทีที่แล้ว", self.html)

    def test_review_reasons_in_thai_and_sorted_first(self):
        for reason in ("สลิปอ่านไม่ได้", "ยอดไม่ตรง", "สลิปซ้ำ", "ต้องตรวจเอง"):
            self.assertIn(reason, self.html)
        self.assertIn("needsReview(b[0]) - needsReview(a[0])", self.html)

    def test_no_slip_approve_asks_first(self):
        self.assertIn("ลูกค้ายังไม่ได้อัปโหลดสลิป เห็นเงินเข้าบัญชีแล้วจริงไหม?", self.html)
        self.assertIn('data-noslip="${o.slipStatus ? "" : "1"}"', self.html)

    def test_mobile_column_labels(self):
        self.assertIn('data-label="เครดิต"', self.html)
        self.assertIn('data-label="ข้อฟรี"', self.html)
        self.assertIn("td[data-label]::before", self.html)

    def test_customer_picker_accepts_any_image(self):
        js = (Path(__file__).resolve().parent.parent / "static" / "app.js").read_text("utf-8")
        self.assertIn('accept="image/*"', js)
