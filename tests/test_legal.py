import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import test_credits as tc  # noqa: E402

STATIC = ROOT / "static"


class LegalContent(unittest.TestCase):
    def test_privacy_covers_required_points(self):
        html = (STATIC / "privacy.html").read_text()
        th, en = html.split('<section lang="en">')
        self.assertLess(html.index('lang="th"'), html.index('lang="en"'))  # Thai first
        for word in ("อีเมล", "รหัสบัญชี Google", "วันเกิด", "SlipOK", "ไม่เก็บรูปสลิป", "Google Gemini", "คุกกี้", "ไม่ขาย", "ivymoonask"):
            self.assertIn(word, th)
        for word in ("email", "Google account ID", "Birth date", "Slip images are not stored", "Gemini", "session cookie",
                     "do not sell", "ivymoonask", "foolmoon.lol"):
            self.assertIn(word, en)

    def test_terms_covers_required_points(self):
        html = (STATIC / "terms.html").read_text()
        for word in ("เพื่อความบันเทิง", "ไม่สามารถขอคืนเงินได้", "ความผิดพลาดในการชำระเงิน", "Fair use",
                     "entertainment only", "non-refundable", "payment errors", "ivymoonask", "Ask the Moon"):
            self.assertIn(word, html)

    def test_pages_are_styled_and_linked(self):
        for name in ("privacy", "terms"):
            html = (STATIC / f"{name}.html").read_text()
            self.assertIn('href="/styles.css"', html)
            self.assertIn(f'<link rel="canonical" href="https://foolmoon.lol/{name}"', html)
            self.assertNotIn("<script", html)
        index = (STATIC / "index.html").read_text()
        footer = re.search(r"<footer>.*?</footer>", index, re.S).group(0)
        self.assertIn('href="/privacy"', footer)
        self.assertIn('href="/terms"', footer)
        js = (STATIC / "app.js").read_text()
        self.assertIn('<a href="/privacy"', js)
        self.assertIn('<a href="/terms"', js)


class LegalRoutes(unittest.TestCase):
    def test_routes_serve_html(self):
        import threading
        import urllib.request
        server = tc.app.ThreadingHTTPServer(("127.0.0.1", 0), tc.app.Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            for path, text in (("/privacy", "นโยบายความเป็นส่วนตัว"), ("/terms", "ข้อกำหนดการใช้งาน")):
                with urllib.request.urlopen(f"http://127.0.0.1:{server.server_address[1]}{path}", timeout=5) as resp:
                    self.assertEqual(resp.status, 200)
                    self.assertIn("text/html", resp.headers["Content-Type"])
                    self.assertIn(text, resp.read().decode())
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
