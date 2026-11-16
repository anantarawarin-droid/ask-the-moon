"""Tarot deck, draws, prompt, fallback, and the served card images."""

import json
import os
import sys
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import app  # noqa: E402
import tarot  # noqa: E402
import test_credits as tc  # noqa: E402

BODY = {"name": "น้ำเพชร", "birthDate": "2006-07-07", "topic": "love", "question": "เขาคิดยังไงกับเรา", "lang": "th"}
POSITION_WORDS = ["past", "present", "future", "อดีต", "ปัจจุบัน", "อนาคต", "position"]


class Deck(unittest.TestCase):
    def test_78_unique_cards(self):
        self.assertEqual(len(tarot.DECK), 78)
        self.assertEqual(len({c["id"] for c in tarot.DECK}), 78)
        self.assertEqual(len({c["nameEn"] for c in tarot.DECK}), 78)
        self.assertEqual(len({c["nameTh"] for c in tarot.DECK}), 78)
        self.assertEqual(sum(c["arcana"] == "major" for c in tarot.DECK), 22)

    def test_every_card_has_image_and_meanings(self):
        sources = json.loads((ROOT / "static/tarot/SOURCES.json").read_text())
        for c in tarot.DECK:
            with self.subTest(card=c["id"]):
                img = ROOT / "static" / tarot.image_path(c["id"]).lstrip("/")
                self.assertTrue(img.is_file())
                head = img.read_bytes()[:12]
                self.assertTrue(head[:4] == b"RIFF" and head[8:12] == b"WEBP")
                self.assertLess(img.stat().st_size, 120_000)
                for k in ("upEn", "revEn", "upTh", "revTh", "nameTh"):
                    self.assertTrue(c[k].strip())
                self.assertEqual(sources[c["id"]]["license"], "Public domain")

    def test_draw_three_distinct_without_positions(self):
        for _ in range(200):
            cards = tarot.draw()
            self.assertEqual(len(cards), 3)
            self.assertEqual(len({c["id"] for c in cards}), 3)
            for c in cards:
                self.assertIsInstance(c["reversed"], bool)
                self.assertNotIn("position", c)
                self.assertNotIn("positionTh", c)
                base = tarot.BY_ID[c["id"]]
                self.assertEqual(c["meaningTh"], base["revTh"] if c["reversed"] else base["upTh"])

    def test_draw_uses_both_orientations_and_many_cards(self):
        seen, orient = set(), set()
        for _ in range(300):
            for c in tarot.draw():
                seen.add(c["id"])
                orient.add(c["reversed"])
        self.assertEqual(orient, {True, False})
        self.assertGreater(len(seen), 70)


class Reading(unittest.TestCase):
    def test_fallback_includes_cards(self):
        with mock.patch.object(app, "llm_generate", return_value=None):
            for lang in ("th", "en"):
                data = app.make_reading({**BODY, "lang": lang})
                self.assertEqual(data["source"], "template")
                cards = data["tarot"]["cards"]
                self.assertEqual(len(cards), 3)
                self.assertEqual(data["tarot"]["headingTh"], "ให้ไพ่เล่าเรื่องราว")
                self.assertEqual(data["tarot"]["headingEn"], "Let the cards tell the story")
                for c in cards:
                    key = "nameTh" if lang == "th" else "nameEn"
                    self.assertIn(c[key], data["reading"])
                    self.assertIn(c["meaningTh" if lang == "th" else "meaningEn"], data["reading"])
                para = tarot.template_paragraph(cards, lang)
                for w in POSITION_WORDS:
                    self.assertNotIn(w, para.lower())

    def test_prompt_has_cards_as_one_story(self):
        seen = {}

        class Resp:
            def read(self):
                return json.dumps({"choices": [{"message": {"content": "บทอ่านทดสอบ"}}]}).encode()
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False

        def fake_urlopen(req, timeout):
            seen["payload"] = json.loads(req.data)
            return Resp()

        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}), \
                mock.patch.object(app.urllib.request, "urlopen", fake_urlopen):
            data = app.make_reading(BODY)
        self.assertEqual(data["source"], "llm")
        prompt = seen["payload"]["messages"][1]["content"]
        for c in data["tarot"]["cards"]:
            self.assertIn(c["nameEn"], prompt)
            self.assertIn(c["nameTh"], prompt)
            self.assertIn(c["meaningTh"], prompt)
        self.assertIn("ONE flowing story", prompt)
        self.assertIn("Thai", prompt)
        card_block = tarot.prompt_lines(data["tarot"]["cards"]).lower()
        for w in POSITION_WORDS:
            self.assertNotIn(w, card_block)


class TarotHttp(tc.Http):
    def test_reading_has_cards_and_images_served(self):
        code, data = self.reading()
        self.assertEqual(code, 200)
        cards = data["tarot"]["cards"]
        self.assertEqual(len(cards), 3)
        for c in cards:
            with urllib.request.urlopen(self.base + c["image"]) as resp:
                self.assertEqual(resp.status, 200)
                self.assertEqual(resp.headers["Content-Type"], "image/webp")
        # Free first question also gets cards; paid ones too.
        self.assertEqual(data["charge"]["kind"], "free")


if __name__ == "__main__":
    unittest.main()
