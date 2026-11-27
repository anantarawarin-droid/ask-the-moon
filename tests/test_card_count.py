"""Customers can choose to draw 1, 2 or 3 cards for tarot and oracle readings."""

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

VISITOR = "c" * 32
BASE = {"name": "น้ำเพชร", "birthDate": "2006-07-07", "topic": "love", "lang": "th",
        "question": "เขาจะกลับมาไหม"}


def _cards(n, deck="tarot"):
    if deck == "oracle":
        return oracle.draw(n)
    return tarot.draw(n)


class ParseAndDraw(unittest.TestCase):
    def test_default_is_three(self):
        params = app.parse_reading_request(BASE)
        self.assertEqual(params["cardCount"], 3)
        self.assertEqual(params["deck"], "tarot")

    def test_accepts_1_2_3(self):
        for n in (1, 2, 3):
            params = app.parse_reading_request({**BASE, "cardCount": n})
            self.assertEqual(params["cardCount"], n)
            params = app.parse_reading_request({**BASE, "cardCount": str(n), "deck": "oracle"})
            self.assertEqual(params["cardCount"], n)

    def test_rejects_bad_counts(self):
        for bad in (0, 4, 5, -1, "two", 1.5, True):
            with self.assertRaises(ValueError):
                app.parse_reading_request({**BASE, "cardCount": bad})

    def test_oracle_draw_honours_count(self):
        for n in (1, 2, 3):
            cards = oracle.draw(n)
            self.assertEqual(len(cards), n)
            self.assertEqual(len({c["id"] for c in cards}), n)
            self.assertTrue(all(c["id"] in oracle.BY_ID for c in cards))

    def test_tarot_draw_honours_count(self):
        for n in (1, 2, 3):
            cards = tarot.draw(n)
            self.assertEqual(len(cards), n)
            self.assertEqual(len({c["id"] for c in cards}), n)

    def test_oracle_headings_follow_count(self):
        self.assertEqual(oracle.heading_th(1), "ไพ่ออราเคิล 1 ใบ")
        self.assertEqual(oracle.heading_en(1), "1 oracle card")
        self.assertEqual(oracle.heading_th(2), "ไพ่ออราเคิล 2 ใบ")
        self.assertEqual(oracle.heading_en(3), "3 oracle cards")
        self.assertEqual(oracle.HEADING_TH, "ไพ่ออราเคิล 3 ใบ")
        self.assertEqual(oracle.HEADING_EN, "3 oracle cards")


class VerdictScale(unittest.TestCase):
    def test_scaled_matches_unscaled_for_three_oracle_cards(self):
        for _ in range(40):
            cards = oracle.draw(3)
            self.assertEqual(oracle.verdict_scaled(cards), oracle.verdict(cards))

    def test_one_strong_oracle_card_can_be_a_yes(self):
        card = oracle._drawn(oracle.BY_ID["oracle-26"])  # Happiness +2
        self.assertEqual(oracle.verdict_scaled([card]), "yes")
        self.assertEqual(oracle.verdict([card]), "likely")

    def test_lone_not_yet_time_stays_not_yet(self):
        card = oracle._drawn(oracle.BY_ID["oracle-08"])
        self.assertEqual(oracle.verdict_scaled([card]), "not_yet")
        self.assertEqual(oracle.verdict([card]), "not_yet")


class Generate(unittest.TestCase):
    def test_each_count_and_deck_draws_that_many(self):
        with mock.patch.object(app, "llm_generate", return_value=None):
            for deck in ("tarot", "oracle"):
                for n in (1, 2, 3):
                    result = app.generate_reading(
                        app.parse_reading_request({**BASE, "deck": deck, "cardCount": n})
                    )
                    cards = result["tarot"]["cards"]
                    self.assertEqual(len(cards), n, (deck, n))
                    if deck == "oracle":
                        self.assertTrue(all(c["id"].startswith("oracle-") for c in cards))
                        self.assertEqual(result["tarot"]["headingTh"], oracle.heading_th(n))
                        self.assertEqual(result["tarot"]["headingEn"], oracle.heading_en(n))
                    else:
                        self.assertTrue(all(not c["id"].startswith("oracle-") for c in cards))
                    self.assertTrue(result["reading"])

    def test_planted_cards_still_ignored_when_count_is_one(self):
        params = app.parse_reading_request({
            **BASE, "deck": "oracle", "cardCount": 1,
            "cards": [{"id": "oracle-01"}, {"id": "oracle-02"}],
        })
        result = app.generate_reading(params)
        self.assertEqual(len(result["tarot"]["cards"]), 1)
        # Even if the planted id happened to be drawn, the request must not require it.
        self.assertTrue(result["tarot"]["cards"][0]["id"].startswith("oracle-"))


class Prompts(unittest.TestCase):
    def test_tarot_prompt_adapts_to_count(self):
        one = app.build_prompt("น้ำเพชร", "love", "เขาจะกลับมาไหม", "th", tarot.draw(1))[1]
        self.assertIn("single message", one)
        self.assertIn("this card", one)
        self.assertNotIn("ONE flowing story", one)
        two = app.build_prompt("น้ำเพชร", "love", "เขาจะกลับมาไหม", "th", tarot.draw(2))[1]
        self.assertIn("the first is the situation", two)
        self.assertIn("the second is the advice", two)
        three = app.build_prompt("น้ำเพชร", "love", "เขาจะกลับมาไหม", "th", tarot.draw(3))[1]
        self.assertIn("ONE flowing story", three)
        self.assertIn("these three cards", three)
        self.assertNotIn("the first is the situation", three)

    def test_oracle_prompt_adapts_to_count(self):
        one = app.build_oracle_prompt("น้ำเพชร", "love", "เขาจะกลับมาไหม", "th", oracle.draw(1))[1]
        self.assertIn("single message", one)
        self.assertIn("this card", one)
        two = app.build_oracle_prompt("น้ำเพชร", "love", "เขาจะกลับมาไหม", "th", oracle.draw(2))[1]
        self.assertIn("the first is the situation", two)
        self.assertIn("the second is the advice", two)
        three = app.build_oracle_prompt("น้ำเพชร", "love", "เขาจะกลับมาไหม", "th", oracle.draw(3))[1]
        self.assertIn("These three Ask the Moon oracle cards are one spread", three)
        self.assertIn("the three cards together", three)
        self.assertNotIn("the first is the situation", three)


class Credits(unittest.TestCase):
    def setUp(self):
        self.old = app.SERVICE
        app.SERVICE = billing.CreditService(billing.JsonStore(tempfile.mkdtemp(prefix="moon-cc-")))

    def tearDown(self):
        app.SERVICE = self.old

    def test_one_and_three_card_readings_cost_the_same_one_credit(self):
        # Use the free question, then two paid readings of different lengths.
        vid = VISITOR
        with mock.patch.object(app, "llm_generate", return_value=("ok", {})):
            first = app.paid_reading({**BASE, "cardCount": 1, "deck": "tarot"}, vid)
            self.assertEqual(first["charge"], {"kind": "free", "charged": True})
            self.assertEqual(len(first["tarot"]["cards"]), 1)
            order = app.SERVICE.create_order(vid, 15)
            app.SERVICE.approve(order["code"])
            # 15 baht is 1 question; buy a second for the 3-card reading.
            order2 = app.SERVICE.create_order(vid, 15)
            app.SERVICE.approve(order2["code"])
            second = app.paid_reading({**BASE, "cardCount": 1, "deck": "oracle"}, vid)
            third = app.paid_reading({**BASE, "cardCount": 3, "deck": "tarot"}, vid)
        self.assertEqual(second["charge"], {"kind": "paid", "charged": True})
        self.assertEqual(third["charge"], {"kind": "paid", "charged": True})
        self.assertEqual(len(second["tarot"]["cards"]), 1)
        self.assertEqual(len(third["tarot"]["cards"]), 3)
        self.assertEqual(app.SERVICE.balance(vid)["credits"], 0)


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
        app.SERVICE = billing.CreditService(billing.JsonStore(tempfile.mkdtemp(prefix="moon-cc-http-")))
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
        code, _, headers = self.req("POST", "/api/auth/signup",
                                    {"username": "count_tester", "password": "moon-pass-123"})
        self.assertEqual(code, 201)
        self.cookie = headers.get("Set-Cookie").split(";")[0]

    def _user_id(self, username="count_tester"):
        with app.SERVICE.store.read() as data:
            for u in data["users"].values():
                if u["username"] == username:
                    return u["id"]
        self.fail("signup did not create the test user")

    def test_http_respects_card_count_for_both_decks(self):
        self.signup()
        uid = self._user_id()
        # Six readings (1/2/3 x two decks): one free question + five paid.
        order = app.SERVICE.create_order(uid, 90)
        app.SERVICE.approve(order["code"])
        with mock.patch.object(app, "llm_generate", return_value=("AI count test", {})):
            for deck in ("tarot", "oracle"):
                for n in (1, 2, 3):
                    code, data, _ = self.req("POST", "/api/reading", {**BASE, "deck": deck, "cardCount": n})
                    self.assertEqual(code, 200, (deck, n, data))
                    self.assertEqual(len(data["tarot"]["cards"]), n)
                    self.assertEqual(data["deck"], deck)
                    self.assertTrue(data["charge"]["charged"])

    def test_http_rejects_invalid_count_without_charging(self):
        self.signup()
        uid = self._user_id()
        before = app.SERVICE.balance(uid)
        code, data, _ = self.req("POST", "/api/reading", {**BASE, "cardCount": 4})
        self.assertEqual(code, 400)
        self.assertIn("1, 2, 3 or 12", data.get("error", ""))
        after = app.SERVICE.balance(uid)
        self.assertEqual(after["credits"], before["credits"])
        self.assertEqual(after["freeAvailable"], before["freeAvailable"])

    def test_oracle_route_stays_404(self):
        status, body, headers = self.req("GET", "/oracle", raw=True)
        self.assertEqual(status, 404)
        self.assertIn("text/html", headers.get("Content-Type", ""))
        self.assertIn("Page not found", body.decode())



if __name__ == "__main__":
    unittest.main()
