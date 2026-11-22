"""Canonical redirects, homepage SEO copy, 404 page, and the site-verification tag."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import test_credits as tc  # noqa: E402
import tarot_pages  # noqa: E402

HTML = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
JS = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
VERIFICATION = '<meta name="google-site-verification" content="CeGm1Qc04OUh2c-3fS746cp97VAdIWcOUM2xhsbnaEk" />'


class HomepageSeo(unittest.TestCase):
    def test_verification_meta_untouched(self):
        self.assertIn(VERIFICATION, HTML)
        self.assertIn('name="google-site-verification"', tc.app.index_html().decode())

    def test_title_and_h1(self):
        title = re.search(r"<title>(.*?)</title>", HTML).group(1)
        self.assertNotIn("foolmoon.lol", title)
        self.assertIn("ไพ่ยิปซี", title)
        self.assertIn("ดูดวงไพ่ทาโรต์ออนไลน์", title)
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", HTML).group(1)
        self.assertIn("ถามจันทร์", h1)
        self.assertIn("ดูดวงไพ่ทาโรต์ออนไลน์", h1)
        self.assertIn("ไพ่ยิปซี", HTML)
        self.assertIn("สำรับเดียวกันทั้ง 78 ใบ", HTML)
        self.assertIn('href="/tarot"', HTML)
        self.assertIn("class=\"meanings-nav\"", HTML)
        self.assertIn("class=\"hero-meanings\"", HTML)

    def test_og_image_is_compressed_jpeg(self):
        from PIL import Image
        self.assertIn("https://foolmoon.lol/og-image.jpg", HTML)
        self.assertNotIn("og-image.png", HTML)
        path = ROOT / "static" / "og-image.jpg"
        with Image.open(path) as im:
            self.assertEqual(im.size, (1200, 630))
            self.assertEqual(im.format, "JPEG")
        self.assertGreaterEqual(path.stat().st_size, 80_000)
        self.assertLessEqual(path.stat().st_size, 150_000)

    def test_faq_and_honest_offer(self):
        self.assertIn("FAQPage", HTML)
        self.assertIn("AggregateOffer", HTML)
        self.assertIn('"lowPrice": "0"', HTML)
        self.assertIn("ถามฟรี 1 ข้อ", HTML)
        self.assertIn('id="faq"', HTML)
        for needle in ("ถามไพ่ฟรีได้ไหม", "ไพ่ยิปซีกับไพ่ทาโรต์", "เปิดไพ่กี่ใบ", "เพื่อความบันเทิง", "พร้อมเพย์"):
            self.assertIn(needle, HTML)

    def test_drawn_card_names_link_in_new_tab(self):
        self.assertIn("function cardMeaningSlug", JS)
        self.assertIn('target="_blank"', JS)
        self.assertIn('href="/tarot/${escapeHtml(slug)}"', JS)
        # Share-image rendering still paints the name as canvas text, not a DOM link.
        share = JS[JS.index("function buildShareCard"):JS.index("function shareCanvasBlob")]
        self.assertNotIn("tcard-link", share)
        self.assertIn('ctx.fillText(name,', share)


class CardMeta(unittest.TestCase):
    def test_all_card_titles_and_descriptions_fit(self):
        for card in tarot_pages.CARDS:
            th, en = tarot_pages.short_th(card), card["nameEn"]
            title = tarot_pages.card_title(th, en)
            desc = tarot_pages.card_description(th, en)
            self.assertTrue(60 <= len(title) <= 70, (len(title), title))
            self.assertTrue(150 <= len(desc) <= 160, (len(desc), en, desc))
            self.assertTrue(title.startswith(f"ความหมายไพ่{th}"))
            self.assertTrue(desc.startswith(f"ความหมายไพ่{th}"))


class CanonicalRedirects(unittest.TestCase):
    def setUp(self):
        import threading
        self.server = tc.app.ThreadingHTTPServer(("127.0.0.1", 0), tc.app.Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.port = self.server.server_address[1]

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def _req(self, path, host=None, method="GET"):
        import http.client
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        headers = {"Host": host} if host else {}
        conn.request(method, path, headers=headers)
        resp = conn.getresponse()
        body = resp.read()
        out = resp.status, resp.getheader("Location") or "", resp.getheader("Content-Type") or "", body
        conn.close()
        return out

    def test_off_canonical_host_redirects(self):
        for path, dest in (
            ("/", "https://foolmoon.lol/"),
            ("/tarot", "https://foolmoon.lol/tarot"),
            ("/tarot/the-fool", "https://foolmoon.lol/tarot/the-fool"),
            ("/index.html", "https://foolmoon.lol/"),
            ("/tarot/?x=1", "https://foolmoon.lol/tarot?x=1"),
            ("/sitemap.xml", "https://foolmoon.lol/sitemap.xml"),
        ):
            status, location, _, body = self._req(path, host="ask-the-moon.onrender.com")
            self.assertEqual(status, 301, path)
            self.assertEqual(location, dest, path)
            self.assertEqual(body, b"", path)

    def test_index_html_and_trailing_slash_on_local_host(self):
        status, location, _, _ = self._req("/index.html")
        self.assertEqual(status, 301)
        self.assertEqual(location, "/")
        status, location, _, _ = self._req("/tarot/")
        self.assertEqual(status, 301)
        self.assertEqual(location, "/tarot")
        status, location, _, _ = self._req("/tarot/the-fool/")
        self.assertEqual(status, 301)
        self.assertEqual(location, "/tarot/the-fool")
        # Root must not redirect.
        status, _, ctype, body = self._req("/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", ctype)
        self.assertIn("ถามจันทร์", body.decode())

    def test_health_on_render_host_is_not_redirected(self):
        status, location, ctype, body = self._req("/api/health", host="ask-the-moon.onrender.com")
        self.assertEqual(status, 200)
        self.assertEqual(location, "")
        self.assertIn("application/json", ctype)
        self.assertIn(b'"ok": true', body)

    def test_canonical_host_still_serves(self):
        status, _, ctype, body = self._req("/sitemap.xml", host="foolmoon.lol")
        self.assertEqual(status, 200)
        self.assertIn("application/xml", ctype)
        self.assertIn(b"<lastmod>", body)

    def test_custom_404(self):
        status, _, ctype, body = self._req("/this-page-does-not-exist")
        html = body.decode()
        self.assertEqual(status, 404)
        self.assertIn("text/html", ctype)
        self.assertIn("ไม่พบหน้านี้", html)
        self.assertIn("Page not found", html)
        self.assertIn('href="/"', html)
        self.assertIn('href="/tarot"', html)
        self.assertIn('name="robots" content="noindex, follow"', html)
        # API 404s stay JSON.
        status, _, ctype, body = self._req("/api/does-not-exist")
        self.assertEqual(status, 404)
        self.assertIn("application/json", ctype)


if __name__ == "__main__":
    unittest.main()
