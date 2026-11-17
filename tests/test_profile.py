"""Birth profile panel (Chinese zodiac, birth-date number, Western zodiac) and saved birth data."""

import json
import sys
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app  # noqa: E402
import birthprofile as bp  # noqa: E402
import test_credits as tc  # noqa: E402


class ProfileMath(unittest.TestCase):
    def test_western_boundaries(self):
        cases = {(1, 19): "capricorn", (1, 20): "aquarius", (2, 18): "aquarius", (2, 19): "pisces",
                 (3, 20): "pisces", (3, 21): "aries", (7, 22): "cancer", (7, 23): "leo",
                 (11, 21): "scorpio", (11, 22): "sagittarius", (12, 21): "sagittarius", (12, 22): "capricorn"}
        for (m, d), sign in cases.items():
            self.assertEqual(bp.western_zodiac(date(2001, m, d)), sign, (m, d))

    def test_chinese_new_year_cusp(self):
        self.assertEqual(bp.chinese_zodiac(date(2006, 1, 28))["key"], "rooster")
        self.assertEqual(bp.chinese_zodiac(date(2006, 1, 29))["key"], "dog")
        self.assertEqual(bp.chinese_zodiac(date(2006, 7, 7))["label_th"], "จอ (สุนัข) ธาตุไฟ")
        self.assertEqual(bp.chinese_zodiac(date(2000, 6, 1))["key"], "dragon")

    def test_number_and_panel(self):
        self.assertEqual(bp.life_path_number(date(2006, 7, 7)), 22)  # master number kept
        self.assertEqual(bp.life_path_number(date(1990, 1, 1)), 3)
        p = bp.build_profile(date(2006, 7, 7), "14:30")
        self.assertEqual(p["dateTh"], "7 กรกฎาคม พ.ศ. 2549")
        self.assertEqual(p["weekdayTh"], "วันศุกร์")
        self.assertEqual((p["western"]["th"], p["chinese"]["lunarYear"], p["number"]["value"]), ("ราศีกรกฎ", 2006, 22))
        for part in ("western", "chinese", "number"):
            self.assertTrue(p[part]["meaningTh"] and p[part]["meaningEn"])
        self.assertEqual(p["hour"]["key"], "afternoon")
        self.assertIsNone(bp.build_profile(date(2006, 7, 7))["hour"])
        for d in (date(1900, 1, 1), date(1999, 12, 31), date(2024, 2, 29)):
            bp.build_profile(d, None)
        self.assertNotIn("ไหวพริธ", json.dumps(bp.ANIMAL_TRAITS, ensure_ascii=False))

    def test_parse_birth(self):
        self.assertEqual(bp.parse_birth("", ""), (None, None))
        self.assertEqual(bp.parse_birth("2006-07-07", ""), (date(2006, 7, 7), None))
        self.assertEqual(bp.parse_birth("2006-07-07", "09:05"), (date(2006, 7, 7), "09:05"))
        for bad_d, bad_t in (("2006-02-30", ""), ("07/07/2006", ""), ("1899-12-31", ""), ("2999-01-01", ""),
                             ("2006-07-07", "25:00"), ("2006-07-07", "9am")):
            with self.assertRaises(ValueError):
                bp.parse_birth(bad_d, bad_t)


class ProfileHttp(tc.Http):
    def test_profile_panel_saved_on_account_and_prompt_clean(self):
        vid = "p" * 32
        h = {"X-Visitor-Id": vid}
        seen = {}

        def fake_llm(*args, **kwargs):
            seen["args"], seen["kwargs"] = args, kwargs
            return None

        with mock.patch.object(app, "llm_generate", side_effect=fake_llm):
            code, data = self.req("POST", "/api/reading", {"name": "น้ำเพชร", "birthDate": "2006-07-07",
                                                           "birthTime": "14:30", "topic": "love",
                                                           "question": "เขาจะกลับมาไหม", "lang": "th"}, h)
        self.assertEqual(code, 200)
        self.assertEqual(data["profile"]["chinese"]["key"], "dog")
        self.assertEqual(data["profile"]["number"]["value"], 22)
        # The AI receives only name, topic, question, language and the cards.
        self.assertEqual(seen["args"], ("น้ำเพชร", "love", "เขาจะกลับมาไหม", "th"))
        self.assertEqual(set(seen["kwargs"]), {"cards", "details"})
        self.assertEqual(seen["kwargs"]["details"], "")
        self.assertNotIn("2006", json.dumps(seen, ensure_ascii=False, default=str))
        # Saved on the account for next time.
        me = self.req("GET", "/api/auth/me", headers=h)[1]
        self.assertEqual(me["birth"], {"date": "2006-07-07", "time": "14:30"})
        # Bad birth date: 400, nothing charged, saved value untouched.
        before = me["freeAvailable"], me["credits"]
        code, _ = self.req("POST", "/api/reading", {"name": "A", "birthDate": "2006-13-01", "topic": "love"}, h)
        self.assertEqual(code, 400)
        me = self.req("GET", "/api/auth/me", headers=h)[1]
        self.assertEqual((me["freeAvailable"], me["credits"]), before)
        self.assertEqual(me["birth"]["date"], "2006-07-07")
        # Without a birth date there's simply no panel.
        data = app.make_reading({"name": "A", "topic": "love", "lang": "th"})
        self.assertIsNone(data["profile"])


@unittest.skipUnless(tc.TEST_PG, "set TEST_DATABASE_URL to run against Postgres")
class PgProfileHttp(ProfileHttp):
    make = staticmethod(tc.pg_service)


if __name__ == "__main__":
    unittest.main()
