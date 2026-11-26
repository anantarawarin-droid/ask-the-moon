"""Anonymous feedback box and the owner-only admin list."""

from __future__ import annotations

import json
import os
import sys
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import app  # noqa: E402
import credits as billing  # noqa: E402
import feedback as moon_feedback  # noqa: E402
import test_credits as tc  # noqa: E402

STATIC = ROOT / "static"
ADMIN = "test-secret-token"
ALLOWED = {"id", "message", "lang", "page", "createdAt"}


class Store(unittest.TestCase):
    def setUp(self):
        self.svc = tc.json_service()

    def test_list_is_newest_first_and_delete_works(self):
        first = self.svc.add_feedback("hello first", "en", "home")
        second = self.svc.add_feedback("สวัสดี", "th", "reading")
        items = self.svc.list_feedback()
        self.assertEqual([x["id"] for x in items], [second["id"], first["id"]])
        self.assertEqual(set(items[0]), ALLOWED)
        self.assertNotIn("ip", items[0])
        self.assertNotIn("userId", items[0])
        self.assertNotIn("visitor", items[0])
        gone = self.svc.delete_feedback(first["id"])
        self.assertEqual(gone["id"], first["id"])
        self.assertEqual([x["id"] for x in self.svc.list_feedback()], [second["id"]])
        with self.assertRaises(billing.PaymentError) as ctx:
            self.svc.delete_feedback(first["id"])
        self.assertEqual(ctx.exception.status, 404)


class Http(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = mock.patch.dict(os.environ, {"ADMIN_TOKEN": ADMIN})
        cls.env.start()
        cls.server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.env.stop()

    def setUp(self):
        app.SERVICE = tc.json_service()
        moon_feedback.BY_IP._hits.clear()

    def req(self, method, path, body=None, headers=None):
        data = json.dumps(body).encode() if body is not None else None
        r = urllib.request.Request(self.base + path, data=data, method=method, headers=headers or {})
        if data:
            r.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(r) as resp:
                raw = resp.read()
                return resp.status, json.loads(raw or b"{}")
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}")

    def admin(self, method, path, body=None, token=ADMIN):
        headers = {"X-Admin-Token": token} if token is not None else {}
        return self.req(method, path, body, headers)

    def test_empty_is_rejected(self):
        status, data = self.req("POST", "/api/feedback", {"message": "   ", "lang": "th"})
        self.assertEqual(status, 400)
        self.assertEqual(data["code"], "empty")
        self.assertIn("พิมพ์ข้อความก่อนส่งนะ", data["error"])
        self.assertEqual(app.SERVICE.list_feedback(), [])

    def test_submit_then_admin_list_and_delete(self):
        status, data = self.req("POST", "/api/feedback", {
            "message": "ชอบธีม Feeling Time ค่ะ",
            "lang": "th",
            "page": "home",
            "ip": "should-be-ignored",
            "userId": "acct_nope",
            "question": "secret question",
        }, {"X-Visitor-Id": "vis_should_not_be_stored", "X-Forwarded-For": "203.0.113.9"})
        self.assertEqual(status, 200)
        self.assertEqual(data, {"ok": True})

        status, data = self.req("GET", "/api/feedback")
        self.assertEqual(status, 404)

        status, data = self.admin("GET", "/api/admin/feedback", token="wrong")
        self.assertEqual(status, 401)

        status, data = self.req("GET", "/api/admin/feedback")
        self.assertEqual(status, 401)

        status, data = self.admin("GET", "/api/admin/feedback")
        self.assertEqual(status, 200)
        self.assertEqual(len(data["items"]), 1)
        item = data["items"][0]
        self.assertEqual(set(item), ALLOWED)
        self.assertEqual(item["message"], "ชอบธีม Feeling Time ค่ะ")
        self.assertEqual(item["lang"], "th")
        self.assertEqual(item["page"], "home")
        blob = json.dumps(item)
        self.assertNotIn("203.0.113.9", blob)
        self.assertNotIn("vis_should_not_be_stored", blob)
        self.assertNotIn("acct_nope", blob)
        self.assertNotIn("secret question", blob)

        status, data = self.admin("POST", f"/api/admin/feedback/{item['id']}/delete")
        self.assertEqual(status, 200)
        self.assertEqual(data["id"], item["id"])
        status, data = self.admin("GET", "/api/admin/feedback")
        self.assertEqual(data["items"], [])

    def test_honeypot_looks_ok_but_is_not_stored(self):
        status, data = self.req("POST", "/api/feedback", {
            "message": "spam", "lang": "en", "website": "https://bots.example",
        })
        self.assertEqual(status, 200)
        self.assertEqual(data, {"ok": True})
        self.assertEqual(app.SERVICE.list_feedback(), [])

    def test_empty_moon_hp_is_stored_but_filled_moon_hp_is_not(self):
        # The public form sends moon_hp (not website) so browser autofill of
        # a field named website cannot silently discard a real note.
        status, data = self.req("POST", "/api/feedback", {
            "message": "ข้อความจริง", "lang": "th", "page": "home", "moon_hp": "",
        })
        self.assertEqual(status, 200)
        self.assertEqual(data, {"ok": True})
        self.assertEqual(len(app.SERVICE.list_feedback()), 1)

        status, data = self.req("POST", "/api/feedback", {
            "message": "should not land", "lang": "en", "moon_hp": "https://foolmoon.lol",
        })
        self.assertEqual(status, 200)
        self.assertEqual(data, {"ok": True})
        self.assertEqual(len(app.SERVICE.list_feedback()), 1)

    def test_rate_limit_and_long_message(self):
        headers = {"X-Forwarded-For": "198.51.100.20"}
        for i in range(3):
            status, data = self.req("POST", "/api/feedback", {"message": f"note {i}", "lang": "en"}, headers)
            self.assertEqual(status, 200, data)
        status, data = self.req("POST", "/api/feedback", {"message": "one too many", "lang": "en"}, headers)
        self.assertEqual(status, 429)
        self.assertEqual(data["code"], "rate_limited")
        self.assertIn("too soon", data["error"])
        self.assertEqual(len(app.SERVICE.list_feedback()), 3)

        moon_feedback.BY_IP._hits.clear()
        status, data = self.req("POST", "/api/feedback", {
            "message": "x" * 600, "lang": "en",
        }, {"X-Forwarded-For": "198.51.100.21"})
        self.assertEqual(status, 200)
        items = app.SERVICE.list_feedback()
        long_ones = [x for x in items if len(x["message"]) == 500]
        self.assertEqual(len(long_ones), 1)
        self.assertEqual(long_ones[0]["message"], "x" * 500)

    def test_script_is_stored_as_text_and_admin_page_escapes(self):
        status, data = self.req("POST", "/api/feedback", {
            "message": '<script>alert("x")</script>', "lang": "en",
        })
        self.assertEqual(status, 200)
        item = self.admin("GET", "/api/admin/feedback")[1]["items"][0]
        self.assertEqual(item["message"], '<script>alert("x")</script>')
        html = (STATIC / "admin.html").read_text(encoding="utf-8")
        self.assertIn("esc(it.message)", html)
        self.assertIn("/api/admin/feedback", html)
        self.assertIn("data-fb-del", html)
        self.assertIn("โหลดข้อความไม่สำเร็จ", html)
        self.assertLess(html.index('id="feedback-card"'), html.index('id="summary"'))

    def test_homepage_and_copy(self):
        import http.client
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_address[1], timeout=5)
        conn.request("GET", "/")
        resp = conn.getresponse()
        html = resp.read().decode()
        self.assertEqual(resp.status, 200)
        conn.close()
        self.assertIn('id="feedback"', html)
        self.assertIn("ฝากความรู้สึกหรือคำแนะนำถึงจันทร์", html)
        self.assertIn('data-i18n="fbSend">ส่ง<', html)
        self.assertIn("ได้รับแล้ว ขอบคุณนะ 🌙", html)
        self.assertIn('id="feedback-hp"', html)
        self.assertIn('name="moon_hp"', html)
        form = html[html.index('id="feedback"'):html.index("</form>", html.index('id="feedback"'))]
        self.assertNotIn('name="website"', form)
        js = (STATIC / "app.js").read_text(encoding="utf-8")
        self.assertIn("moon_hp:", js)
        self.assertNotIn("website: hp", js)
        self.assertIn('fbTitle: "ฝากความรู้สึกหรือคำแนะนำถึงจันทร์"', js)
        self.assertIn('fbTitle: "Leave a feeling or a suggestion for the Moon"', js)
        self.assertIn('fbOk: "Received — thank you 🌙"', js)
        self.assertIn('fbSend: "Send"', js)
        # Customer copy must stay warm and free of backend talk.
        for phrase in ("rate limit", "honeypot", "IP address", "ที่อยู่ไอพี", "เซิร์ฟเวอร์"):
            self.assertNotIn(phrase, html)
        form = html[html.index('id="feedback"'):html.index("</form>", html.index('id="feedback"'))]
        for phrase in ("rate limit", "honeypot", "IP", "เซิร์ฟเวอร์", "ฐานข้อมูล"):
            self.assertNotIn(phrase, form)


if __name__ == "__main__":
    unittest.main()
