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

BODY = {"name": "น้ำเพชร", "birthDate": "2006-07-07", "birthTime": "14:30", "topic": "love", "question": "เขาคิดยังไงกับเรา", "lang": "th"}
POSITION_WORDS = ["past:", "present:", "future:", "past —", "present —", "future —", "อดีต:", "ปัจจุบัน:",
                  "อนาคต:", "อดีต —", "ปัจจุบัน —", "อนาคต —", "position", "ตำแหน่ง"]


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
                img = ROOT / "static" / tarot.image_path(c["id"]).split("?")[0].lstrip("/")
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
                    name = c["nameTh"].split(" (")[0] if lang == "th" else c["nameEn"]
                    self.assertIn(name, data["reading"])
                    self.assertIn(c["meaningTh" if lang == "th" else "meaningEn"], data["reading"])
                for w in POSITION_WORDS:
                    self.assertNotIn(w, data["reading"].lower())

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
        full = json.dumps(seen["payload"], ensure_ascii=False).lower()
        for banned in ("2006", "07-07", "birth date:", "birth time /", "western zodiac:", "chinese zodiac:",
                       "life path number", "ราศี", "นักษัตร", "cancer", "dog", "ปีจอ"):
            self.assertNotIn(banned, full)
        self.assertIn("First sentence: the clear answer", prompt)
        self.assertIn(tarot.VERDICT_HINT_EN[tarot.verdict(data["tarot"]["cards"])], prompt)
        self.assertNotIn("chart", data)
        for banned in ("14:30", "afternoon", "ยามบ่าย", "master builder", "ปรมาจารย์"):
            self.assertNotIn(banned, full)
        # The birth data shows up only in the separate profile panel.
        self.assertEqual(data["profile"]["western"]["key"], "cancer")
        card_block = tarot.prompt_lines(data["tarot"]["cards"]).lower()
        for w in POSITION_WORDS:
            self.assertNotIn(w, card_block)


class DirectAnswers(unittest.TestCase):
    def card(self, cid, rev=False):
        c = tarot.BY_ID[cid]
        return {"id": cid, "nameEn": c["nameEn"], "nameTh": c["nameTh"], "reversed": rev,
                "meaningEn": c["revEn"] if rev else c["upEn"], "meaningTh": c["revTh"] if rev else c["upTh"],
                "image": tarot.image_path(cid)}

    def test_verdicts(self):
        good = [self.card("major-19"), self.card("cups-10"), self.card("wands-06")]
        bad = [self.card("major-16"), self.card("swords-10"), self.card("cups-05")]
        mixed = [self.card("major-19"), self.card("major-16"), self.card("cups-03", True)]
        self.assertEqual(tarot.verdict(good), "yes")
        self.assertEqual(tarot.verdict(bad), "no")
        self.assertIn(tarot.verdict(mixed), ("not_yet", "unlikely"))

    def test_fallback_is_direct_and_cards_only(self):
        bad = [self.card("major-16"), self.card("swords-10"), self.card("cups-05")]
        text = tarot.fallback_reading("น้ำเพชร", "เขาจะกลับมาหาเราไหม", "ความรัก", "love", bad, "th")
        first = text.split("\n")[0]
        self.assertIn("ไม่ค่ะ", first)
        for banned in ("ราศี", "นักษัตร", "เลขศาสตร์", "วันเกิด", "เวลาเกิด", "ขึ้นอยู่กับตัวคุณ"):
            self.assertNotIn(banned, text)
        self.assertIn("คำแนะนำ", text)
        good = [self.card("major-19"), self.card("cups-10"), self.card("wands-06")]
        self.assertIn("ใช่ค่ะ", tarot.fallback_reading("A", "งานใหม่ที่สมัครไว้จะได้ไหม", "การงาน", "career", good, "th"))
        en = tarot.fallback_reading("Nam", "Will he come back?", "love", "love", bad, "en")
        self.assertIn("no", en.split("\n")[0].lower())

    def test_yes_no_detection(self):
        self.assertTrue(tarot.is_yes_no("งานใหม่ที่สมัครไว้จะได้ไหม"))
        self.assertTrue(tarot.is_yes_no("เขาจะกลับมาหาเราไหม?"))
        self.assertFalse(tarot.is_yes_no("เขาคิดยังไงกับเรา"))
        self.assertTrue(tarot.is_yes_no("Will I get the job?"))

    def test_premium_from_cards_only(self):
        prem = tarot.premium_from_cards(tarot.draw(), "th")
        self.assertEqual(set(prem), {"forecast", "gift", "shadow", "compatibility", "numbers", "colors", "day"})
        blob = json.dumps(prem, ensure_ascii=False)
        for banned in ("ราศี", "นักษัตร", "ปี"):
            self.assertNotIn(banned + "จอ", blob)

    def test_birth_fields_not_required(self):
        data = app.make_reading({"name": "น้ำเพชร", "topic": "career", "question": "ได้งานไหม", "lang": "th"})
        self.assertEqual(len(data["tarot"]["cards"]), 3)


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
