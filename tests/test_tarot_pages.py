"""Crawlable tarot meaning pages (/tarot, /tarot/<slug>), robots and sitemap."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import test_credits as tc  # noqa: E402
import tarot  # noqa: E402
import tarot_meanings  # noqa: E402
import tarot_pages  # noqa: E402


class MeaningsData(unittest.TestCase):
    def test_every_card_has_full_thai_meanings(self):
        self.assertEqual(len(tarot.DECK), 78)
        self.assertEqual(set(tarot_meanings.MEANINGS), {c["id"] for c in tarot.DECK})
        for cid, parts in tarot_meanings.MEANINGS.items():
            self.assertEqual(len(parts), 5, cid)
            for text in parts:
                self.assertRegex(text, r"[\u0E00-\u0E7F]", cid)
                self.assertGreater(len(text), 25, cid)

    def test_slugs_unique_and_readable(self):
        self.assertEqual(len(set(tarot_pages.SLUGS)), 78)
        for slug in ("the-fool", "wheel-of-fortune", "ace-of-cups", "king-of-pentacles", "the-world"):
            self.assertIn(slug, tarot_pages.BY_SLUG)


class PagesOverHttp(unittest.TestCase):
    def setUp(self):
        import threading
        self.server = tc.app.ThreadingHTTPServer(("127.0.0.1", 0), tc.app.Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.port = self.server.server_address[1]

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def _req(self, path, method="GET"):
        import http.client
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request(method, path)
        resp = conn.getresponse()
        body = resp.read()
        out = resp.status, resp.getheader("Content-Type") or "", body
        conn.close()
        return out

    def test_robots(self):
        status, ctype, body = self._req("/robots.txt")
        text = body.decode()
        self.assertEqual(status, 200)
        self.assertIn("Disallow: /api/", text)
        self.assertIn("Disallow: /admin", text)
        self.assertIn("Sitemap: https://foolmoon.lol/sitemap.xml", text)
        self.assertNotIn("Disallow: /tarot", text)

    def test_sitemap_has_every_card_page(self):
        status, _, body = self._req("/sitemap.xml")
        text = body.decode()
        self.assertEqual(status, 200)
        for slug in tarot_pages.SLUGS:
            self.assertIn(f"<loc>https://foolmoon.lol/tarot/{slug}</loc>", text)
        self.assertNotIn("/admin", text)
        self.assertNotIn("/api/", text)

    def test_index_lists_all_cards(self):
        status, ctype, body = self._req("/tarot")
        html = body.decode()
        self.assertEqual(status, 200)
        self.assertIn("text/html", ctype)
        self.assertIn('<link rel="canonical" href="https://foolmoon.lol/tarot" />', html)
        self.assertIn('<html lang="th">', html)
        self.assertIn("ไพ่ยิปซี", html)
        self.assertIn("สำรับเดียวกันทั้ง 78 ใบ", html)
        self.assertEqual(len(set(re.findall(r'href="/tarot/([a-z0-9-]+)"', html))), 78)
        self.assertIn('href="/#oracle"', html)
        for card in tarot_pages.CARDS:
            self.assertIn(tarot.thumb_path(card["id"]), html)
            self.assertNotIn(tarot.image_path(card["id"]), html)
            self.assertRegex(html, rf'src="{re.escape(tarot.thumb_path(card["id"]))}" alt="ไพ่[^"]+" width="150" height="\d+"')
        self.assertEqual(self._req("/tarot/")[0], 301)

    def test_card_pages(self):
        for slug, th, en in (("the-fool", "คนโง่", "The Fool"), ("three-of-cups", "สามถ้วย", "Three of Cups")):
            status, ctype, body = self._req(f"/tarot/{slug}")
            html = body.decode()
            self.assertEqual(status, 200, slug)
            self.assertIn("text/html", ctype)
            title = re.search(r"<title>(.*?)</title>", html).group(1)
            self.assertIn(f"ความหมายไพ่{th}", title)
            self.assertIn(en, title)
            self.assertGreaterEqual(len(title), 60, title)
            self.assertLessEqual(len(title), 70, title)
            self.assertIn(f'<link rel="canonical" href="https://foolmoon.lol/tarot/{slug}" />', html)
            desc = re.search(r'<meta name="description" content="([^"]+)"', html).group(1)
            self.assertGreaterEqual(len(desc), 150, desc)
            self.assertLessEqual(len(desc), 160, desc)
            self.assertIn("กลับหัว", html)
            for topic in ("ความรัก", "การงาน", "การเงิน"):
                self.assertIn(topic, html)
            self.assertIn('href="/#oracle"', html)
            self.assertIn("application/ld+json", html)
            card = tarot_pages.BY_SLUG[slug]
            self.assertIn(tarot.image_path(card["id"]), html)
            self.assertNotIn(tarot.thumb_path(card["id"]), html)

    def test_card_images_and_unknown_slugs_still_static(self):
        status, ctype, _ = self._req("/tarot/major-00.webp")
        self.assertEqual(status, 200)
        self.assertIn("image/webp", ctype)
        status, ctype, _ = self._req("/tarot/major-00-thumb.webp")
        self.assertEqual(status, 200)
        self.assertIn("image/webp", ctype)
        self.assertEqual(self._req("/tarot/not-a-card")[0], 404)

    def test_head_requests(self):
        for path in ("/tarot", "/tarot/the-fool", "/robots.txt", "/sitemap.xml"):
            status, _, body = self._req(path, "HEAD")
            self.assertEqual(status, 200, path)
            self.assertEqual(body, b"", path)

    def test_home_links_to_meanings(self):
        html = (ROOT / "static" / "index.html").read_text()
        self.assertIn('href="/tarot"', html)
        self.assertIn('application/ld+json', html)
        self.assertIn('og:image', html)


if __name__ == "__main__":
    unittest.main()
