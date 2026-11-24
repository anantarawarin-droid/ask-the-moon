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
        for word in ("อีเมล", "รหัสบัญชี Google", "วันเกิด", "SlipOK", "ไม่เก็บรูปสลิป", "Google Gemini", "คุกกี้", "ไม่ขาย", "ivymoonask",
                     "เราไม่เก็บคำถาม ไพ่ที่จั่วได้ หรือคำทำนาย"):
            self.assertIn(word, th)
        for word in ("email", "Google account ID", "Birth date", "Slip images are not stored", "Gemini", "session cookie",
                     "do not sell", "ivymoonask", "foolmoon.lol",
                     "Questions, drawn cards, and readings are not stored"):
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
        self.assertIn('<link rel="canonical" href="https://foolmoon.lol/"', index)
        footer = re.search(r"<footer>.*?</footer>", index, re.S).group(0)
        self.assertIn('href="/privacy"', footer)
        self.assertIn('href="/terms"', footer)
        self.assertIn('data-i18n="noHistory">ไม่มีการเก็บประวัติการใช้งาน<', footer)
        self.assertIn('data-i18n="noHistoryResult">ไม่มีการเก็บประวัติการดูดวง · แคปเก็บไว้ได้เอง<', index)
        js = (STATIC / "app.js").read_text()
        self.assertIn('noHistoryResult: "Reading history is not saved · Screenshot to keep"', js)
        self.assertIn('noHistory: "No reading history is stored"', js)
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


class SearchConsole(unittest.TestCase):
    def setUp(self):
        import threading
        self.server = tc.app.ThreadingHTTPServer(("127.0.0.1", 0), tc.app.Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.port = self.server.server_address[1]

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def _get(self, path, host=None):
        import http.client
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        headers = {"Host": host} if host else {}
        conn.request("GET", path, headers=headers)
        resp = conn.getresponse()
        body = resp.read().decode()
        ctype = resp.getheader("Content-Type")
        status = resp.status
        conn.close()
        return status, ctype, body

    def test_robots_txt_allows_all_and_blocks_admin_and_api(self):
        status, ctype, body = self._get("/robots.txt")
        self.assertEqual(status, 200)
        self.assertEqual(ctype, "text/plain")
        self.assertIn("User-agent: *", body)
        self.assertIn("Allow: /", body)
        self.assertIn("Disallow: /admin", body)
        self.assertIn("Disallow: /api/", body)
        self.assertIn("Disallow: /oracle", body)
        self.assertIn("Sitemap: https://foolmoon.lol/sitemap.xml", body)

    def test_sitemap_lists_public_pages_on_canonical_host(self):
        status, ctype, body = self._get("/sitemap.xml", host="foolmoon.lol")
        self.assertEqual(status, 200)
        self.assertEqual(ctype, "application/xml")
        self.assertIn('xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"', body)
        for url in ("https://foolmoon.lol/", "https://foolmoon.lol/privacy", "https://foolmoon.lol/terms"):
            self.assertIn(f"<loc>{url}</loc>", body)
        self.assertNotIn("onrender.com", body)
        # 3 site pages + the /tarot index + 78 card pages (oracle catalog is private)
        self.assertEqual(body.count("<url>"), 3 + 1 + 78)
        self.assertEqual(body.count("<lastmod>"), 3 + 1 + 78)
        self.assertIn("<loc>https://foolmoon.lol/tarot</loc>", body)
        self.assertNotIn("<loc>https://foolmoon.lol/oracle</loc>", body)
        self.assertIn("<loc>https://foolmoon.lol/tarot/the-fool</loc>", body)
        self.assertRegex(body, r"<lastmod>\d{4}-\d{2}-\d{2}</lastmod>")

    def test_public_pages_still_load(self):
        for path, needle in (("/", "ถามจันทร์"), ("/privacy", "นโยบายความเป็นส่วนตัว"), ("/terms", "ข้อกำหนดการใช้งาน")):
            status, ctype, body = self._get(path)
            self.assertEqual(status, 200, path)
            self.assertIn("text/html", ctype)
            self.assertIn(needle, body)
            self.assertIn('rel="canonical"', body)


ICON_LINKS = (
    '<link rel="icon" href="/favicon.ico" sizes="any">',
    '<link rel="icon" type="image/svg+xml" href="/favicon.svg">',
    '<link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png">',
    '<link rel="apple-touch-icon" href="/apple-touch-icon.png">',
    '<link rel="manifest" href="/site.webmanifest">',
)

ICON_FILES = {
    "/favicon.ico": ("image/x-icon", None),
    "/favicon.svg": ("image/svg+xml", None),
    "/favicon-48.png": ("image/png", (48, 48)),
    "/favicon-192.png": ("image/png", (192, 192)),
    "/apple-touch-icon.png": ("image/png", (180, 180)),
    "/icon-512.png": ("image/png", (512, 512)),
    "/site.webmanifest": ("application/manifest+json", None),
}


class Favicons(unittest.TestCase):
    def test_html_points_at_real_icon_files(self):
        for name in ("index.html", "terms.html", "privacy.html"):
            html = (STATIC / name).read_text()
            self.assertNotIn("data:image/svg+xml", html, name)
            for link in ICON_LINKS:
                self.assertIn(link, html, name)

    def test_icon_files_exist_with_expected_sizes(self):
        from PIL import Image, IcoImagePlugin
        svg = (STATIC / "favicon.svg").read_text()
        self.assertIn('fill="#0a0614"', svg)
        self.assertIn('fill="#d4af37"', svg)
        self.assertIn("rx=\"12\"", svg)
        self.assertIn("M38 10a22 22 0 1 0 12 36A18 18 0 1 1 38 10z", svg)
        for path, size in (("favicon-48.png", (48, 48)), ("favicon-192.png", (192, 192)),
                           ("apple-touch-icon.png", (180, 180)), ("icon-512.png", (512, 512))):
            with Image.open(STATIC / path) as im:
                self.assertEqual(im.size, size, path)
        with (STATIC / "favicon.ico").open("rb") as fh:
            self.assertEqual(sorted(IcoImagePlugin.IcoFile(fh).sizes()), [(16, 16), (32, 32), (48, 48)])

    def test_icons_are_served_with_types_and_cache(self):
        import http.client
        import threading
        server = tc.app.ThreadingHTTPServer(("127.0.0.1", 0), tc.app.Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            port = server.server_address[1]
            for path, (ctype, _) in ICON_FILES.items():
                conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                conn.request("GET", path)
                resp = conn.getresponse()
                body = resp.read()
                self.assertEqual(resp.status, 200, path)
                self.assertEqual(resp.getheader("Content-Type"), ctype, path)
                self.assertEqual(resp.getheader("Cache-Control"), "public, max-age=31536000, immutable", path)
                self.assertGreater(len(body), 0, path)
                conn.close()
        finally:
            server.shutdown()
            server.server_close()




if __name__ == "__main__":
    unittest.main()
