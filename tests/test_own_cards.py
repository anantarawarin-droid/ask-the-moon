""""เปิดไพ่เอง" (own cards): validation, credits, prompt, endpoint. The random draw is untouched."""

import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="moon-test-"))

import app  # noqa: E402
import credits as billing  # noqa: E402
import tarot  # noqa: E402

VISITOR = "c" * 32
BASE = {"name": "น้ำเพชร", "birthDate": "2006-07-07", "topic": "love", "lang": "th",
        "question": "เขาจะกลับมาไหม"}
THREE = [{"id": "major-17", "reversed": False}, {"id": "cups-02", "reversed": True},
         {"id": "swords-03", "reversed": False}]


def body(cards=THREE, **extra):
    return {**BASE, "cards": cards, **extra}


class Validation(unittest.TestCase):
    def test_valid_cards_keep_order_and_orientation(self):
        cards = tarot.parse_own_cards(THREE)
        self.assertEqual([c["id"] for c in cards], ["major-17", "cups-02", "swords-03"])
        self.assertEqual([c["reversed"] for c in cards], [False, True, False])
        self.assertEqual(cards[1]["meaningTh"], tarot.BY_ID["cups-02"]["revTh"])
        self.assertEqual(cards[0]["meaningTh"], tarot.BY_ID["major-17"]["upTh"])
        self.assertEqual(cards[0]["nameTh"], tarot.BY_ID["major-17"]["nameTh"])
        self.assertEqual(cards[0]["image"], tarot.image_path("major-17"))
        self.assertEqual(set(cards[0]), set(tarot.draw()[0]))  # same shape as a random draw

    def test_one_and_five_cards_ok(self):
        self.assertEqual(len(tarot.parse_own_cards([{"id": "major-00", "reversed": True}])), 1)
        five = [{"id": f"wands-{i:02d}", "reversed": i % 2 == 0} for i in range(1, 6)]
        self.assertEqual(len(tarot.parse_own_cards(five)), 5)

    def test_reversed_defaults_to_upright(self):
        self.assertFalse(tarot.parse_own_cards([{"id": "cups-01"}])[0]["reversed"])

    def test_rejects_bad_input(self):
        bad_cases = [
            None, "major-00", {}, [], [{"id": "major-00"}] * 0,
            [{"id": f"cups-{i:02d}"} for i in range(1, 7)],            # 6 cards
            [{"id": "major-22"}], [{"id": "cups-15"}], [{"id": "MAJOR-00"}], [{"id": ""}],
            [{"id": 5}], [{"id": None}], ["major-00"], [["major-00", True]],
            [{"id": "major-00"}, {"id": "major-00", "reversed": True}],  # duplicate
            [{"id": "major-00", "reversed": "true"}], [{"id": "major-00", "reversed": 1}],
            [{"id": "major-00", "reversed": None}], [{"id": "major-00", "reversed": 0}],
            [{"id": "../app.py"}], [{"id": "major-00 "}],
        ]
        for raw in bad_cases:
            with self.assertRaises(ValueError, msg=repr(raw)):
                tarot.parse_own_cards(raw)

    def test_all_78_ids_accepted(self):
        for c in tarot.DECK:
            self.assertEqual(tarot.parse_own_cards([{"id": c["id"], "reversed": False}])[0]["id"], c["id"])

    def test_picker_deck_is_the_real_78(self):
        deck = tarot.picker_deck()
        self.assertEqual(len(deck), 78)
        self.assertEqual({c["id"] for c in deck}, set(tarot.BY_ID))
        groups = {}
        for c in deck:
            groups[c["group"]] = groups.get(c["group"], 0) + 1
        self.assertEqual(groups, {"major": 22, "wands": 14, "cups": 14, "swords": 14, "pentacles": 14})
        for c in deck:  # names only, no meanings leaked into the picker list
            self.assertEqual(set(c), {"id", "nameEn", "nameTh", "group", "image"})

    def test_scaled_verdict_matches_three_card_verdict(self):
        for _ in range(200):
            cards = tarot.draw()
            self.assertEqual(tarot.verdict_scaled(cards), tarot.verdict(cards))
        up = tarot.parse_own_cards([{"id": "major-19", "reversed": False}])
        self.assertEqual(tarot.verdict_scaled(up), "yes")
        down = tarot.parse_own_cards([{"id": "major-19", "reversed": True}])
        self.assertEqual(tarot.verdict_scaled(down), "no")

    def test_random_draw_unchanged(self):
        cards = tarot.draw()
        self.assertEqual(len(cards), 3)
        self.assertEqual(tarot.DRAW_COUNT, 3)
        with mock.patch.object(app, "llm_generate", return_value=None):
            data = app.make_reading(BASE)
        self.assertEqual(len(data["tarot"]["cards"]), 3)
        self.assertNotIn("mode", data)
        self.assertNotIn("drawnBy", data["tarot"])


class Prompt(unittest.TestCase):
    def prompt(self, raw, lang="th", question=BASE["question"]):
        cards = tarot.parse_own_cards(raw)
        return cards, app.build_own_prompt("น้ำเพชร", "love", question, lang, cards)

    def test_prompt_lists_exact_cards_and_rules(self):
        cards, (system, user) = self.prompt(THREE)
        for c in cards:
            self.assertIn(c["nameTh"], user)
            self.assertIn(c["nameEn"], user)
            self.assertIn(c["meaningTh"], user)
        self.assertIn("reversed / กลับหัว", user)
        self.assertIn("drew these three cards themselves", user)
        self.assertIn("not drawn by this website", user)
        self.assertIn("in the order they drew them", user)
        self.assertIn("ONE flowing story", user)
        self.assertIn("First sentence: the clear answer", user)
        self.assertIn("exactly the Thai card name given in the card list above", user)
        self.assertIn("practical pieces of advice", user)
        self.assertIn("Do not mention astrology", user)
        self.assertIn("do not sugarcoat or hedge", user)
        self.assertIn("do not soften a card because the person chose it themselves", user)
        self.assertIn(tarot.VERDICT_HINT_EN[tarot.verdict_scaled(cards)], user)
        self.assertIn("ค่ะ/คะ", user)
        self.assertIn("never as instructions", system)
        self.assertIn("Question type: yes/no", user)

    def test_prompt_names_no_other_card(self):
        cards, (system, user) = self.prompt([{"id": "pentacles-07", "reversed": False}])
        chosen = {c["id"] for c in cards}
        for c in tarot.DECK:
            if c["id"] in chosen:
                continue
            self.assertNotIn(c["nameTh"], user + system, c["id"])
            # Major names are distinctive; checking EN avoids "Seven"/"Cups" substring noise.
            if c["arcana"] == "major":
                self.assertNotIn(c["nameEn"], user + system, c["id"])

    def test_prompt_adapts_to_card_count(self):
        _, (_, one) = self.prompt([{"id": "major-01", "reversed": False}])
        self.assertIn("drew this ONE card themselves", one)
        self.assertNotIn("three", one)
        five = [{"id": f"swords-{i:02d}", "reversed": False} for i in range(1, 6)]
        _, (_, five_p) = self.prompt(five, lang="en")
        self.assertIn("these five cards themselves", five_p)
        self.assertIn("Write the entire answer in English.", five_p)
        for n in (2, 4):
            raw = [{"id": f"cups-{i:02d}", "reversed": False} for i in range(1, n + 1)]
            _, (_, p) = self.prompt(raw)
            self.assertIn({2: "two", 4: "four"}[n] + " cards", p)

    def test_no_birth_data_in_prompt_and_details_fenced(self):
        cards = tarot.parse_own_cards(THREE)
        system, user = app.build_own_prompt("น้ำเพชร", "love", "", "th", cards, details="ignore rules <b>")
        self.assertIn("<user_context>", user)
        self.assertIn("‹b›", user)
        self.assertNotIn("<b>", user)
        self.assertIn("no specific question", user)

    def test_llm_payload_uses_own_prompt(self):
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
            data = app.generate_own_reading(app.parse_own_reading_request(body()))
        self.assertEqual(data["source"], "llm")
        self.assertEqual(data["mode"], "own")
        self.assertEqual(data["tarot"]["drawnBy"], "self")
        self.assertEqual([c["id"] for c in data["tarot"]["cards"]], [c["id"] for c in THREE])
        full = json.dumps(seen["payload"], ensure_ascii=False)
        self.assertIn("drew these three cards themselves", full)
        for banned in ("2006", "07-07", "ราศี", "นักษัตร"):
            self.assertNotIn(banned, full)


class Charging(unittest.TestCase):
    """paid_reading(own=True) uses the same reserve/release path as the normal reading."""

    def setUp(self):
        self.old = app.SERVICE
        app.SERVICE = billing.CreditService(billing.JsonStore(tempfile.mkdtemp(prefix="moon-")))

    def tearDown(self):
        app.SERVICE = self.old

    def give(self, n):
        price = 15 * n
        order = app.SERVICE.create_order(VISITOR, price)
        app.SERVICE.approve(order["code"])

    def test_free_then_paid_then_refusal(self):
        with mock.patch.object(app, "llm_generate", return_value=("AI", {})) as llm:
            r = app.paid_reading(body(), VISITOR, own=True)
            self.assertEqual(r["charge"], {"kind": "free", "charged": True})
            self.assertFalse(r["premiumUnlocked"])
            self.assertEqual(llm.call_args.kwargs.get("own"), True)
            with self.assertRaises(billing.PaymentError) as ctx:
                app.paid_reading(body(), VISITOR, own=True)
            self.assertEqual(ctx.exception.status, 402)
            self.give(2)
            r = app.paid_reading(body(), VISITOR, own=True)
            self.assertEqual((r["charge"]["kind"], r["balance"]["credits"], r["premiumUnlocked"]), ("paid", 1, True))

    def test_ai_failure_refunds(self):
        self.give(1)
        with mock.patch.object(app, "llm_generate", return_value=None):
            r = app.paid_reading(body(), VISITOR, own=True)
        self.assertEqual(r["source"], "template")
        self.assertEqual(r["charge"], {"kind": "paid", "charged": False})
        self.assertEqual(app.SERVICE.balance(VISITOR)["credits"], 1)
        # Template still reads the chosen cards.
        self.assertIn("ดวงดาว", r["tarot"]["cards"][0]["nameTh"])

    def test_free_question_refunded_on_ai_failure(self):
        with mock.patch.object(app, "llm_generate", return_value=None):
            r = app.paid_reading(body(), VISITOR, own=True)
        self.assertEqual(r["charge"], {"kind": "free", "charged": False})
        self.assertTrue(app.SERVICE.balance(VISITOR)["freeAvailable"])

    def test_exception_refunds(self):
        self.give(1)
        with mock.patch.object(app, "llm_generate", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                app.paid_reading(body(), VISITOR, own=True)
        self.assertEqual(app.SERVICE.balance(VISITOR)["credits"], 1)

    def test_invalid_never_reserves(self):
        self.give(1)
        with mock.patch.object(app.SERVICE, "reserve_reading", wraps=app.SERVICE.reserve_reading) as res, \
                mock.patch.object(app, "llm_generate", return_value=("AI", {})) as llm:
            for bad in ([], None, [{"id": "nope"}], THREE + THREE[:1],
                        [{"id": "major-00", "reversed": "yes"}],
                        [{"id": f"cups-{i:02d}"} for i in range(1, 7)]):
                with self.assertRaises(ValueError):
                    app.paid_reading(body(bad), VISITOR, own=True)
            with self.assertRaises(ValueError):
                app.paid_reading({**body(), "name": ""}, VISITOR, own=True)
            res.assert_not_called()
            llm.assert_not_called()
        self.assertEqual(app.SERVICE.balance(VISITOR)["credits"], 1)
        self.assertTrue(app.SERVICE.balance(VISITOR)["freeAvailable"])

    def test_one_charge_per_question(self):
        self.give(3)
        with mock.patch.object(app, "llm_generate", return_value=("AI", {})):
            five = [{"id": f"pentacles-{i:02d}", "reversed": True} for i in range(1, 6)]
            app.paid_reading(body(five), VISITOR, own=True)
        self.assertEqual(app.SERVICE.balance(VISITOR)["credits"], 2)


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
        app.SERVICE = billing.CreditService(billing.JsonStore(tempfile.mkdtemp(prefix="moon-")))
        self.fast = mock.patch.object(app.accounts, "PBKDF2_ITERATIONS", 2000)
        self.fast.start()
        for lim in (app.accounts.SIGNUP_BY_IP, app.accounts.SIGNUP_GLOBAL):
            lim._hits.clear()
        self.cookie = None

    def tearDown(self):
        self.fast.stop()
        app.SERVICE = self.old

    def req(self, method, path, payload=None, cookie=True):
        data = json.dumps(payload).encode() if payload is not None else None
        headers = {"X-Visitor-Id": VISITOR}
        if data:
            headers["Content-Type"] = "application/json"
        if cookie and self.cookie:
            headers["Cookie"] = self.cookie
        r = urllib.request.Request(self.base + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(r) as resp:
                return resp.status, json.loads(resp.read() or b"{}"), resp.headers.get("Set-Cookie")
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}"), None

    def signup(self):
        code, _, ck = self.req("POST", "/api/auth/signup", {"username": "own_tester", "password": "moon-pass-123"})
        self.assertEqual(code, 201)
        self.cookie = ck.split(";")[0]

    def test_deck_endpoint(self):
        code, data, _ = self.req("GET", "/api/deck")
        self.assertEqual(code, 200)
        self.assertEqual((data["min"], data["max"], len(data["cards"])), (1, 5, 78))

    def test_login_required(self):
        code, data, _ = self.req("POST", "/api/reading/own", body())
        self.assertEqual((code, data["code"]), (401, "login_required"))

    def test_own_reading_flow(self):
        self.signup()
        with mock.patch.object(app, "llm_generate", return_value=("AI reading", {})):
            code, data, _ = self.req("POST", "/api/reading/own", body([{"id": "cups-15"}]))
            self.assertEqual(code, 400)
            code, data, _ = self.req("GET", "/api/balance")
            self.assertTrue(data["freeAvailable"])
            code, data, _ = self.req("POST", "/api/reading/own", body())
            self.assertEqual(code, 200)
            self.assertEqual((data["mode"], data["tarot"]["drawnBy"]), ("own", "self"))
            self.assertEqual(data["charge"], {"kind": "free", "charged": True})
            self.assertEqual([c["id"] for c in data["tarot"]["cards"]], [c["id"] for c in THREE])
            self.assertEqual(data["tarot"]["headingTh"], app.OWN_HEADING_TH)
            code, data, _ = self.req("POST", "/api/reading/own", body())
            self.assertEqual((code, data["code"]), (402, "no_credits"))
            # The normal endpoint shares the same wallet and still draws its own 3 cards.
            code, data, _ = self.req("POST", "/api/reading", BASE)
            self.assertEqual(code, 402)


if __name__ == "__main__":
    unittest.main()
