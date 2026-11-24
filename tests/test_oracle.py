"""37-card Ask the Moon oracle: catalog, draw, credits, pages, and assets."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="moon-test-"))

import app  # noqa: E402
import credits as billing  # noqa: E402
import oracle  # noqa: E402
import tarot  # noqa: E402

VISITOR = "o" * 32
BASE = {"name": "น้ำเพชร", "birthDate": "2006-07-07", "topic": "love", "lang": "th",
        "question": "เขาจะกลับมาไหม", "deck": "oracle"}


class Catalog(unittest.TestCase):
    def test_exactly_37_unique_cards_in_three_categories(self):
        self.assertEqual(len(oracle.DECK), 37)
        self.assertEqual(len({c["id"] for c in oracle.DECK}), 37)
        self.assertEqual([c["id"] for c in oracle.DECK], [f"oracle-{i:02d}" for i in range(1, 38)])
        counts = {cat: len(cards) for cat, cards in oracle.BY_CATEGORY.items()}
        self.assertEqual(counts, {"time": 8, "emotion": 19, "words": 10})
        for card in oracle.DECK:
            self.assertTrue(card["nameEn"] and card["nameTh"])
            self.assertTrue(card["meaningEn"] and card["meaningTh"])
            self.assertTrue(card["textEn"] and card["textTh"])
            self.assertGreaterEqual(len(card["textTh"]), 40)
            self.assertGreaterEqual(len(card["textEn"]), 40)
            self.assertNotIn("الخطوة", card["textTh"])
            self.assertNotIn("swearing", card["textTh"])
            banned = (
                "คุยทับ", "ความจริงที่จืดกว่า",
                "เรื่องนี้เป็นทางยาว ไกลกว่าหนึ่งปี",
                "อยู่บนนาฬิกาที่ยาวกว่า", "คลี่คลายเป็นฤดูกาล",
                "การรั่วของเวลา", "การไร้เกราะ", "เดินหลับ",
                "เรื่องที่ยืมมา", "เมื่อพื้นจริง ๆ", "วางเท้าใต้ฝัน",
                "ความซื่อจะเจ็บ", "งานที่ซื่อ", "จิตกำลังซ้อม",
                "ระบบประสาท", "ตกผล", "จุดโหวง",
            )
            blob = " ".join(card[k] for k in ("nameTh", "meaningTh", "textTh"))
            for phrase in banned:
                self.assertNotIn(phrase, blob, f"{card['id']} still has {phrase!r}")

    def test_assets_exist_and_are_lightweight(self):
        static = ROOT / "static" / "oracle"
        sizes = []
        for card in oracle.DECK:
            full = static / f"{card['id']}.webp"
            thumb = static / f"{card['id']}-thumb.webp"
            self.assertTrue(full.is_file(), full)
            self.assertTrue(thumb.is_file(), thumb)
            self.assertLessEqual(full.stat().st_size, 60 * 1024, full)
            self.assertLessEqual(thumb.stat().st_size, 16 * 1024, thumb)
            self.assertGreater(thumb.stat().st_size, 2 * 1024)
            sizes.append(full.stat().st_size)
            self.assertEqual(oracle.image_path(card["id"]), f"/oracle/{card['id']}.webp?v={oracle.IMAGE_VERSION}")
            self.assertEqual(oracle.thumb_path(card["id"]), f"/oracle/{card['id']}-thumb.webp?v={oracle.THUMB_VERSION}")
        self.assertLess(sum(sizes), 2_000_000)
        for name in ("card-back.webp", "card-back-thumb.webp"):
            path = static / name
            self.assertTrue(path.is_file(), path)
            self.assertLess(path.stat().st_size, 40 * 1024)

    def test_draw_is_one_of_each_category_and_ignores_client_ids(self):
        seen = {cat: set() for cat in oracle.CATEGORIES}
        leans = set()
        for _ in range(400):
            cards = oracle.draw()
            self.assertEqual(len(cards), 3)
            self.assertEqual([c["category"] for c in cards], ["time", "emotion", "words"])
            self.assertEqual([c["position"] for c in cards], ["time", "emotion", "words"])
            self.assertTrue(all(c["reversed"] is False for c in cards))
            self.assertTrue(all(c["image"] == oracle.image_path(c["id"]) for c in cards))
            self.assertEqual(len({c["id"] for c in cards}), 3)
            for c in cards:
                seen[c["category"]].add(c["id"])
            leans.add(oracle.verdict(cards))
        # Every card in every category should appear over 80 structured draws.
        for cat, ids in seen.items():
            self.assertEqual(ids, {c["id"] for c in oracle.BY_CATEGORY[cat]}, cat)
        self.assertTrue(leans <= {"yes", "likely", "not_yet", "unlikely", "no"})
        self.assertGreaterEqual(len(leans), 2)

    def test_not_yet_time_blocks_a_clear_yes(self):
        time_c = oracle.BY_ID["oracle-08"]  # Not Yet Time
        feel = oracle.BY_ID["oracle-26"]    # Happiness (+2)
        words = oracle.BY_ID["oracle-20"]   # Love to Give is emotion; use a positive words card
        words = oracle.BY_ID["oracle-30"]
        cards = [
            {**oracle.public_card(time_c), "position": "time"},
            {**oracle.public_card(feel), "position": "emotion"},
            {**oracle.public_card(words), "position": "words"},
        ]
        self.assertEqual(oracle.verdict(cards), "not_yet")


    def test_result_cards_omit_oracle_meanings(self):
        js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
        self.assertIn('${oracleCard ? "" : `<span class="tcard-meaning">${escapeHtml(meaning)}</span>`}', js)
        self.assertIn('${oracleCard ? "" : `<small class="tcard-sub">${escapeHtml(sub)}</small>`}', js)

    def test_category_labels_are_short_thai(self):
        self.assertEqual(oracle.HEADING_TH, "เวลา · อารมณ์ · คำพูด")
        self.assertEqual(oracle.CATEGORIES["time"]["th"], "เวลา")
        self.assertEqual(oracle.CATEGORIES["emotion"]["th"], "อารมณ์")
        self.assertEqual(oracle.CATEGORIES["words"]["th"], "คำพูด")


class Reading(unittest.TestCase):
    def setUp(self):
        self.old = app.SERVICE
        app.SERVICE = billing.CreditService(billing.JsonStore(tempfile.mkdtemp(prefix="moon-orc-")))

    def tearDown(self):
        app.SERVICE = self.old

    def test_generate_uses_oracle_spread_and_ignores_planted_cards(self):
        params = app.parse_reading_request({**BASE, "cards": [{"id": "oracle-01"}, {"id": "major-00"}]})
        self.assertEqual(params["deck"], "oracle")
        result = app.generate_reading(params)
        self.assertEqual(result["deck"], "oracle")
        cards = result["tarot"]["cards"]
        self.assertEqual(len(cards), 3)
        self.assertEqual([c["category"] for c in cards], ["time", "emotion", "words"])
        self.assertNotEqual([c["id"] for c in cards], ["oracle-01", "major-00"])
        self.assertEqual(result["tarot"]["headingTh"], "เวลา · อารมณ์ · คำพูด")
        self.assertIn(result["reading"], [result["reading"]])  # non-empty
        self.assertTrue(result["reading"])
        self.assertEqual(result["premium"]["kind"], "oracle")
        self.assertEqual(result["premium"]["numbers"], [])

    def test_unknown_deck_rejected(self):
        with self.assertRaises(ValueError):
            app.parse_reading_request({**BASE, "deck": "poker"})

    def test_default_deck_is_still_tarot(self):
        body = {k: v for k, v in BASE.items() if k != "deck"}
        params = app.parse_reading_request(body)
        self.assertEqual(params["deck"], "tarot")
        result = app.generate_reading(params)
        self.assertEqual(result["deck"], "tarot")
        self.assertTrue(all(not c["id"].startswith("oracle-") for c in result["tarot"]["cards"]))

    def test_credits_match_tarot_and_own_oracle_is_rejected(self):
        vid = VISITOR
        with mock.patch.object(app, "llm_generate", return_value=("AI oracle", {})):
            first = app.paid_reading(BASE, vid)
        self.assertEqual(first["deck"], "oracle")
        self.assertEqual(first["charge"], {"kind": "free", "charged": True})
        with self.assertRaises(ValueError):
            app.paid_reading({**BASE, "cards": [{"id": "major-00", "reversed": False}]}, vid, own=True)
        # Free preview already used; paid credit required, same wallet as tarot.
        order = app.SERVICE.create_order(vid, 15)
        app.SERVICE.approve(order["code"])
        with mock.patch.object(app, "llm_generate", return_value=("AI oracle 2", {})):
            second = app.paid_reading(BASE, vid)
        self.assertEqual(second["charge"], {"kind": "paid", "charged": True})
        self.assertEqual(app.SERVICE.balance(vid)["credits"], 0)
        with mock.patch.object(app, "llm_generate", return_value=("AI tarot", {})):
            with self.assertRaises(billing.PaymentError) as ctx:
                app.paid_reading({"name": "A", "birthDate": "2006-07-07", "topic": "love", "lang": "th"}, vid)
        self.assertEqual(ctx.exception.status, 402)

    def test_template_fallback_is_free(self):
        with mock.patch.object(app, "llm_generate", return_value=None):
            result = app.paid_reading(BASE, VISITOR + "1")
        self.assertEqual(result["source"], "template")
        self.assertFalse(result["charge"]["charged"])
        self.assertTrue(app.SERVICE.balance(VISITOR + "1")["freeAvailable"])


class Http(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        self.old = app.SERVICE
        app.SERVICE = billing.CreditService(billing.JsonStore(tempfile.mkdtemp(prefix="moon-orc-http-")))
        self.fast = mock.patch.object(app.accounts, "PBKDF2_ITERATIONS", 2000)
        self.fast.start()
        for lim in (app.accounts.SIGNUP_BY_IP, app.accounts.SIGNUP_GLOBAL):
            lim._hits.clear()
        self.cookie = None

    def tearDown(self):
        self.fast.stop()
        app.SERVICE = self.old

    def req(self, method, path, payload=None, cookie=True, raw=False):
        import urllib.error
        import urllib.request
        data = json.dumps(payload).encode() if payload is not None else None
        headers = {"X-Visitor-Id": VISITOR}
        if data:
            headers["Content-Type"] = "application/json"
        if cookie and self.cookie:
            headers["Cookie"] = self.cookie
        r = urllib.request.Request(self.base + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(r) as resp:
                body = resp.read()
                if raw:
                    return resp.status, body, resp.headers
                return resp.status, json.loads(body or b"{}"), resp.headers
        except urllib.error.HTTPError as e:
            body = e.read()
            if raw:
                return e.code, body, e.headers
            return e.code, json.loads(body or b"{}"), None

    def signup(self):
        code, _, headers = self.req("POST", "/api/auth/signup", {"username": "oracle_tester", "password": "moon-pass-123"})
        self.assertEqual(code, 201)
        self.cookie = headers.get("Set-Cookie").split(";")[0]

    def test_oracle_catalog_is_not_public(self):
        code, data, _ = self.req("GET", "/api/oracle")
        self.assertEqual(code, 200)
        self.assertEqual(data.get("ok"), True)
        self.assertEqual(data.get("back"), oracle.back_path())
        self.assertNotIn("cards", data)
        self.assertNotIn("count", data)
        blob = json.dumps(data, ensure_ascii=False)
        for card in oracle.DECK:
            self.assertNotIn(card["id"], blob)
            self.assertNotIn(card["nameTh"], blob)
            self.assertNotIn(card["nameEn"], blob)
        status, body, headers = self.req("GET", "/oracle", raw=True)
        html = body.decode()
        self.assertEqual(status, 404)
        self.assertIn("text/html", headers.get("Content-Type", ""))
        self.assertIn("Page not found", html)
        self.assertNotIn("ไพ่ออราเคิลถามจันทร์ 37 ใบ", html)
        for card in oracle.DECK:
            self.assertNotIn(card["nameTh"], html)
            self.assertNotIn(f'id="{card["id"]}"', html)
        # Directory must not list the card files.
        self.assertNotIn(".webp", html)
        self.assertIn("CeGm1Qc04OUh2c-3fS746cp97VAdIWcOUM2xhsbnaEk", (ROOT / "static" / "index.html").read_text(encoding="utf-8"))

    def test_assets_are_immutable(self):
        for path in (oracle.image_path("oracle-01"), oracle.thumb_path("oracle-01"), oracle.back_path()):
            status, body, headers = self.req("GET", path, raw=True)
            self.assertEqual(status, 200, path)
            self.assertEqual(headers.get("Cache-Control"), "public, max-age=31536000, immutable")
            self.assertIn("image/webp", headers.get("Content-Type", ""))
            self.assertGreater(len(body), 2000)

    def test_reading_http_flow_and_planted_cards_ignored(self):
        self.signup()
        planted = {**BASE, "cards": [{"id": "oracle-01"}, {"id": "oracle-02"}, {"id": "oracle-03"}]}
        with mock.patch.object(app, "llm_generate", return_value=("AI oracle http", {})):
            code, data, _ = self.req("POST", "/api/reading", planted)
        self.assertEqual(code, 200)
        self.assertEqual(data["deck"], "oracle")
        ids = [c["id"] for c in data["tarot"]["cards"]]
        self.assertEqual(len(ids), 3)
        # Server randomization: planted identities must not be trusted.
        # They may coincide rarely; the draw is still 1-per-category.
        self.assertEqual([c["category"] for c in data["tarot"]["cards"]], ["time", "emotion", "words"])
        self.assertTrue(all(c["image"] == oracle.image_path(c["id"]) for c in data["tarot"]["cards"]))
        self.assertEqual(data["charge"]["kind"], "free")

    def test_homepage_has_pick_ui_and_does_not_lose_verification(self):
        status, body, _ = self.req("GET", "/", raw=True)
        html = body.decode()
        self.assertEqual(status, 200)
        self.assertIn('name="google-site-verification" content="CeGm1Qc04OUh2c-3fS746cp97VAdIWcOUM2xhsbnaEk"', html)
        self.assertIn('id="pick-table"', html)
        self.assertIn('id="deck-oracle"', html)
        self.assertIn("มีไพ่อยู่แล้ว", html)
        self.assertIn('data-i18n="modeDraw">เลือกไพ่<', html)
        self.assertIn('data-i18n="modeDrawSub">แตะเลือก 3 ใบ<', html)
        js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
        self.assertIn('modeDraw: "เลือกไพ่"', js)
        self.assertIn('modeDrawSub: "แตะเลือก 3 ใบ"', js)
        self.assertIn('modeDraw: "Pick cards"', js)
        self.assertIn('modeDrawSub: "Tap 3 cards"', js)
        self.assertIn('deck: ownMode ? "tarot" : state.deckKind', js)
        self.assertIn('pickTitle: "เลือกไพ่ 3 ใบ"', js)
        self.assertIn('pickHint: "แตะเลือกไพ่ 3 ใบ"', js)
        self.assertIn('pickTitle: "Pick 3 cards"', js)
        self.assertIn('pickHint: "Tap 3 cards"', js)
        for phrase in ("สุ่มไพ่จริง", "ไม่ใช่ใบที่เห็นตอนคว่ำ", "คว่ำหน้า", "สุ่มไพ่ให้ตอนเปิด",
                       "the Moon draws the actual cards", "not the backs you see now",
                       "facedown cards", "Pick 3 facedown"):
            self.assertNotIn(phrase, html)
            self.assertNotIn(phrase, js)
        self.assertNotIn("heroLede: \"ดูดวงไพ่ทาโรต์ 3 ใบ ตอบตรง ๆ + โปรไฟล์", js)
        self.assertNotIn('href="/oracle"', html)
        self.assertNotIn('href="/oracle#', js)
        self.assertIn('cardBack: "/oracle/card-back.webp?v=1"', js)


if __name__ == "__main__":
    unittest.main()
