"""Reading jobs: a charged reading is never lost. The answer is held briefly in memory, handed over once it is
picked up, and the credits are refunded exactly once if it never is (or the job fails / the server restarts)."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="moon-test-"))

import app  # noqa: E402
import credits as billing  # noqa: E402
from test_credits import TEST_PG, pg_service  # noqa: E402

VISITOR = "e" * 32
OTHER = "f" * 32
BASE = {"name": "น้ำเพชร", "birthDate": "2006-07-07", "lang": "th", "question": "งานนี้จะไปทางไหน"}
JOB = "job" + "a" * 29
JOB2 = "job" + "b" * 29


def later() -> float:
    return time.time() + 3600  # past every deadline, but before billing rows are forgotten (2 days)


def give(credits: int, free_used: bool = True, vid: str = VISITOR):
    if hasattr(app.SERVICE, "store"):
        with app.SERVICE.store.transaction() as data:
            v = app.SERVICE._visitor(data, vid)
            v["credits"] = credits
            v["freeUsed"] = free_used
        return
    with app.SERVICE._tx() as cur:
        cur.execute("INSERT INTO moon_visitors (id, credits, free_used) VALUES (%s, %s, %s) "
                    "ON CONFLICT (id) DO UPDATE SET credits = EXCLUDED.credits, free_used = EXCLUDED.free_used",
                    (vid, credits, free_used))


def credits_of(vid: str = VISITOR) -> int:
    return app.SERVICE.balance(vid)["credits"]


def wait_done(job_id: str, vid: str = VISITOR, tries: int = 200) -> dict:
    for _ in range(tries):
        out = app.poll_reading_job(job_id, vid)
        if out["status"] != "working":
            return out
        time.sleep(0.02)
    raise AssertionError("job never finished")


def settled(job_id: str) -> None:
    for _ in range(200):
        with app.JOBS_LOCK:
            job = app.JOBS.get(job_id)
        if job is None or job["status"] != "working":
            return
        time.sleep(0.02)
    raise AssertionError("job never settled")


class JobsBase:
    make = staticmethod(lambda: billing.CreditService(billing.JsonStore(tempfile.mkdtemp(prefix="moon-jobs-"))))

    def setUp(self):
        self.old = app.SERVICE
        app.SERVICE = self.make()
        with app.JOBS_LOCK:
            app.JOBS.clear()
        self.llm = mock.patch.object(app, "llm_generate", return_value=("ผลการอ่านไพ่", {}))
        self.llm.start()

    def tearDown(self):
        self.llm.stop()
        app.SERVICE = self.old
        with app.JOBS_LOCK:
            app.JOBS.clear()

    def start(self, job_id=JOB, vid=VISITOR, **extra):
        return app.start_reading_job({**BASE, "cardCount": 12, "jobId": job_id, **extra}, vid)

    # -- the happy path ---------------------------------------------------------------
    def test_delivered_answer_keeps_the_charge_and_is_dropped_after_ack(self):
        give(25)
        out = self.start()
        self.assertEqual(out["status"], "working")
        self.assertEqual(credits_of(), 5)  # taken up front
        done = wait_done(JOB)
        self.assertEqual(done["status"], "done")
        self.assertEqual(len(done["result"]["tarot"]["cards"]), 12)
        self.assertEqual(done["result"]["charge"], {"kind": "paid", "charged": True, "cost": 20})
        self.assertEqual(done["result"]["balance"]["credits"], 5)
        self.assertEqual(app.SERVICE.reservation(JOB)["state"], "delivered")
        again = app.poll_reading_job(JOB, VISITOR)  # a lost response can be fetched again, free
        self.assertEqual(again["status"], "done")
        app.ack_reading_job(JOB, VISITOR)
        self.assertNotIn(JOB, app.JOBS)
        self.assertEqual(app.poll_reading_job(JOB, VISITOR)["status"], "gone")
        self.assertEqual(credits_of(), 5)
        self.assertEqual(app.sweep_reading_jobs(later()), [])  # delivered is final: never refunded
        self.assertEqual(credits_of(), 5)

    def test_retried_start_with_the_same_id_never_charges_twice(self):
        give(45)
        self.start()
        self.start()
        self.assertEqual(credits_of(), 25)
        wait_done(JOB)
        self.start()  # still the same job (answer held in memory)
        self.assertEqual(credits_of(), 25)
        app.ack_reading_job(JOB, VISITOR)
        self.start()  # memory forgotten but the billing row remembers
        self.assertEqual(credits_of(), 25)

    def test_not_enough_credits_creates_nothing(self):
        give(19)
        with self.assertRaises(billing.PaymentError) as ctx:
            self.start()
        self.assertEqual((ctx.exception.status, ctx.exception.code), (402, "not_enough_credits"))
        self.assertEqual(credits_of(), 19)
        self.assertNotIn(JOB, app.JOBS)
        self.assertIsNone(app.SERVICE.reservation(JOB))

    def test_bad_job_id_is_rejected_before_any_charge(self):
        give(25)
        for bad in (None, "", "short", "x" * 100, "has space " + "a" * 20):
            with self.assertRaises(ValueError):
                app.start_reading_job({**BASE, "cardCount": 12, "jobId": bad}, VISITOR)
        self.assertEqual(credits_of(), 25)

    # -- never picked up -> refund once --------------------------------------------------
    def test_answer_never_picked_up_is_refunded_once(self):
        give(25)
        self.start()
        settled(JOB)
        self.assertEqual(app.SERVICE.reservation(JOB)["state"], "charged")
        self.assertEqual(app.sweep_reading_jobs(time.time() + 60), [])  # still waiting for pickup
        self.assertEqual(credits_of(), 5)
        self.assertEqual(app.sweep_reading_jobs(time.time() + billing.PICKUP_SECONDS + 5), [JOB])
        self.assertEqual(credits_of(), 25)
        self.assertEqual(app.sweep_reading_jobs(later()), [])  # no second refund
        self.assertEqual(credits_of(), 25)
        out = app.poll_reading_job(JOB, VISITOR)
        self.assertEqual(out["status"], "refunded")
        self.assertNotIn("result", out)  # the answer is gone: refund OR answer, never both
        self.assertEqual(credits_of(), 25)

    def test_picked_up_then_swept_is_not_refunded(self):
        give(25)
        self.start()
        wait_done(JOB)
        self.assertEqual(app.sweep_reading_jobs(later()), [])
        self.assertEqual(credits_of(), 5)

    def test_sweeper_wins_the_race_against_pickup(self):
        give(25)
        self.start()
        settled(JOB)
        self.assertEqual(app.SERVICE.refund_due_reservations(later()), [JOB])  # sweeper refunds first
        out = app.poll_reading_job(JOB, VISITOR)  # memory still holds the answer: it must not be handed over
        self.assertEqual(out["status"], "refunded")
        self.assertNotIn("result", out)
        self.assertEqual(credits_of(), 25)

    def test_pickup_wins_the_race_against_sweeper(self):
        give(25)
        self.start()
        settled(JOB)
        self.assertEqual(app.poll_reading_job(JOB, VISITOR)["status"], "done")
        self.assertEqual(app.SERVICE.refund_due_reservations(later()), [])
        self.assertFalse(app.SERVICE.refund_reservation(JOB))
        self.assertEqual(credits_of(), 5)

    # -- failures ------------------------------------------------------------------------
    def test_generation_error_refunds(self):
        give(25)
        with mock.patch.object(app, "llm_generate", side_effect=RuntimeError("boom")):
            self.start()
            self.assertEqual(wait_done(JOB)["status"], "refunded")
        self.assertEqual(credits_of(), 25)
        self.assertEqual(app.sweep_reading_jobs(later()), [])
        self.assertEqual(credits_of(), 25)

    def test_ai_unavailable_hands_over_the_backup_reading_free(self):
        give(25)
        with mock.patch.object(app, "llm_generate", return_value=None):
            self.start()
            done = wait_done(JOB)
        self.assertEqual(done["status"], "done")
        self.assertEqual(done["result"]["source"], "template")
        self.assertFalse(done["result"]["charge"]["charged"])
        self.assertEqual(credits_of(), 25)
        self.assertEqual(app.poll_reading_job(JOB, VISITOR)["status"], "done")
        self.assertEqual(app.sweep_reading_jobs(later()), [])
        self.assertEqual(credits_of(), 25)

    def test_free_preview_is_given_back_too(self):
        give(0, free_used=False)
        with mock.patch.object(app, "llm_generate", side_effect=RuntimeError("boom")):
            app.start_reading_job({**BASE, "cardCount": 1, "jobId": JOB}, VISITOR)
            self.assertEqual(wait_done(JOB)["status"], "refunded")
        self.assertTrue(app.SERVICE.balance(VISITOR)["freeAvailable"])

    def test_job_that_overruns_is_refunded_and_its_late_answer_is_dropped(self):
        give(25)
        gate = threading.Event()

        def slow(*_a, **_k):
            gate.wait(10)
            return ("late answer", {})

        with mock.patch.object(app, "llm_generate", side_effect=slow):
            self.start()
            self.assertEqual(app.sweep_reading_jobs(time.time() + billing.RESERVE_RUN_SECONDS + 5), [JOB])
            self.assertEqual(credits_of(), 25)
            gate.set()
            settled(JOB)
        for _ in range(100):
            if app.SERVICE.reservation(JOB)["state"] == "refunded":
                break
            time.sleep(0.02)
        self.assertEqual(app.SERVICE.reservation(JOB)["state"], "refunded")
        self.assertEqual(app.poll_reading_job(JOB, VISITOR)["status"], "refunded")
        self.assertEqual(credits_of(), 25)

    # -- process restart (memory lost) ------------------------------------------------------
    def test_restart_while_generating_refunds_after_the_deadline(self):
        give(25)
        app.SERVICE.reserve_job(JOB, VISITOR, 20)  # the old process took the credits, then died
        self.assertEqual(credits_of(), 5)
        self.assertEqual(app.poll_reading_job(JOB, VISITOR)["status"], "working")  # young: maybe still running
        self.assertEqual(app.sweep_reading_jobs(time.time() + 10), [])
        self.assertEqual(app.sweep_reading_jobs(time.time() + billing.RESERVE_RUN_SECONDS + 5), [JOB])
        self.assertEqual(credits_of(), 25)
        self.assertEqual(app.poll_reading_job(JOB, VISITOR)["status"], "refunded")
        self.assertEqual(credits_of(), 25)

    def test_restart_after_finishing_refunds_when_the_customer_comes_back(self):
        give(25)
        app.SERVICE.reserve_job(JOB, VISITOR, 20)
        self.assertTrue(app.SERVICE.advance_reservation(JOB, "reserved", "charged", deadline_in=600))
        out = app.poll_reading_job(JOB, VISITOR)  # the answer was only in memory: lost
        self.assertEqual(out["status"], "refunded")
        self.assertEqual(credits_of(), 25)
        self.assertEqual(app.poll_reading_job(JOB, VISITOR)["status"], "refunded")
        self.assertEqual(app.sweep_reading_jobs(later()), [])
        self.assertEqual(credits_of(), 25)

    def test_restart_after_delivery_is_never_refunded(self):
        give(25)
        self.start()
        wait_done(JOB)
        with app.JOBS_LOCK:
            app.JOBS.clear()  # restart
        self.assertEqual(app.poll_reading_job(JOB, VISITOR)["status"], "gone")
        self.assertEqual(app.sweep_reading_jobs(later()), [])
        self.assertEqual(credits_of(), 5)

    # -- safety ----------------------------------------------------------------------------
    def test_other_customers_cannot_read_ack_or_reuse_a_job(self):
        give(25)
        give(25, vid=OTHER)
        self.start()
        settled(JOB)
        for call in (lambda: app.poll_reading_job(JOB, OTHER),):
            with self.assertRaises(billing.PaymentError) as ctx:
                call()
            self.assertEqual(ctx.exception.status, 404)
        app.ack_reading_job(JOB, OTHER)  # ignored
        app.poll_reading_job(JOB, VISITOR)
        self.assertIn(JOB, app.JOBS)
        with self.assertRaises(billing.PaymentError) as ctx:
            self.start(vid=OTHER)
        self.assertEqual((ctx.exception.status, ctx.exception.code), (409, "job_conflict"))
        self.assertEqual(credits_of(OTHER), 25)
        with app.JOBS_LOCK:
            app.JOBS.clear()
        with self.assertRaises(billing.PaymentError) as ctx:  # row-level check after a restart
            self.start(vid=OTHER)
        self.assertEqual(ctx.exception.code, "job_conflict")
        with self.assertRaises(billing.PaymentError) as ctx:
            app.poll_reading_job(JOB, OTHER)
        self.assertEqual(ctx.exception.status, 404)

    def test_ack_before_delivery_does_not_drop_the_answer(self):
        give(25)
        self.start()
        settled(JOB)
        app.ack_reading_job(JOB, VISITOR)
        self.assertIn(JOB, app.JOBS)
        self.assertEqual(app.poll_reading_job(JOB, VISITOR)["status"], "done")

    def test_unknown_job_is_404(self):
        for jid in ("nope" * 6, "x" * 5):
            with self.assertRaises(billing.PaymentError) as ctx:
                app.poll_reading_job(jid, VISITOR)
            self.assertEqual(ctx.exception.status, 404)

    def test_the_database_never_holds_the_reading(self):
        give(25)
        with mock.patch.object(app, "llm_generate", return_value=("SECRET-READING-TEXT", {})):
            self.start(question="SECRET-QUESTION")
            wait_done(JOB)
        row = app.SERVICE.reservation(JOB)
        self.assertEqual(set(row) - {"jobId", "updatedAt"}, {"visitor", "kind", "cost", "state", "deadline"})
        if hasattr(app.SERVICE, "store"):
            blob = json.dumps(app.SERVICE.store._data, ensure_ascii=False)
            self.assertNotIn("SECRET-READING-TEXT", blob)
            self.assertNotIn("SECRET-QUESTION", blob)

    def test_too_many_running_jobs_per_visitor(self):
        give(100)
        gate = threading.Event()
        with mock.patch.object(app, "llm_generate", side_effect=lambda *a, **k: (gate.wait(10), ("x", {}))[1]):
            for i in range(app.MAX_JOBS_PER_VISITOR):
                app.start_reading_job({**BASE, "cardCount": 1, "jobId": f"many{i}" + "z" * 20}, VISITOR)
            with self.assertRaises(billing.PaymentError) as ctx:
                app.start_reading_job({**BASE, "cardCount": 1, "jobId": "many9" + "z" * 20}, VISITOR)
            self.assertEqual(ctx.exception.code, "too_many_jobs")
            gate.set()
            for i in range(app.MAX_JOBS_PER_VISITOR):
                settled(f"many{i}" + "z" * 20)
        self.assertEqual(credits_of(), 100 - app.MAX_JOBS_PER_VISITOR)

    def test_purge_forgets_old_final_rows_only(self):
        give(25)
        self.start()
        wait_done(JOB)
        app.SERVICE.reserve_job(JOB2, VISITOR, 1)
        self.assertEqual(app.SERVICE.purge_reservations(now=time.time() + 10), 0)
        self.assertEqual(app.SERVICE.purge_reservations(now=time.time() + billing.JOB_ROW_KEEP_SECONDS + 10), 1)
        self.assertIsNone(app.SERVICE.reservation(JOB))
        self.assertIsNotNone(app.SERVICE.reservation(JOB2))  # still open: kept so it can be refunded


class JsonJobs(JobsBase, unittest.TestCase):
    pass


@unittest.skipUnless(TEST_PG, "set TEST_DATABASE_URL to run against Postgres")
class PgJobs(JobsBase, unittest.TestCase):
    make = staticmethod(pg_service)

    def test_concurrent_refunds_credit_once(self):
        give(25)
        app.SERVICE.reserve_job(JOB, VISITOR, 20)
        wins = []
        threads = [threading.Thread(target=lambda: wins.append(app.SERVICE.refund_reservation(JOB))) for _ in range(12)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        self.assertEqual(sum(wins), 1)
        self.assertEqual(credits_of(), 25)

    def test_concurrent_starts_with_one_id_charge_once(self):
        give(45)
        created = []
        threads = [threading.Thread(target=lambda: created.append(app.SERVICE.reserve_job(JOB, VISITOR, 20)["created"]))
                   for _ in range(12)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        self.assertEqual(sum(created), 1)
        self.assertEqual(credits_of(), 25)


class JobsOverHttp(unittest.TestCase):
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
        app.SERVICE = billing.CreditService(billing.JsonStore(tempfile.mkdtemp(prefix="moon-jobs-http-")))
        self.fast = mock.patch.object(app.accounts, "PBKDF2_ITERATIONS", 2000)
        self.fast.start()
        for lim in (app.accounts.SIGNUP_BY_IP, app.accounts.SIGNUP_GLOBAL):
            lim._hits.clear()
        with app.JOBS_LOCK:
            app.JOBS.clear()
        self.cookie = None

    def tearDown(self):
        self.fast.stop()
        app.SERVICE = self.old

    def req(self, method, path, payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        headers = {"X-Visitor-Id": VISITOR}
        if data:
            headers["Content-Type"] = "application/json"
        if self.cookie:
            headers["Cookie"] = self.cookie
        r = urllib.request.Request(self.base + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(r) as resp:
                return resp.status, json.loads(resp.read() or b"{}"), resp.headers
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}"), None

    def signup(self):
        code, _, headers = self.req("POST", "/api/auth/signup", {"username": "job_tester", "password": "moon-pass-123"})
        self.assertEqual(code, 201)
        self.cookie = headers.get("Set-Cookie").split(";")[0]
        with app.SERVICE.store.read() as data:
            return next(u["id"] for u in data["users"].values() if u["username"] == "job_tester")

    def test_login_required(self):
        self.assertEqual(self.req("POST", "/api/reading", {**BASE, "jobId": JOB})[0], 401)
        self.assertEqual(self.req("GET", f"/api/reading/job/{JOB}")[0], 401)
        self.assertEqual(self.req("POST", f"/api/reading/job/{JOB}/ack", {})[0], 401)

    def test_start_poll_ack_over_http(self):
        uid = self.signup()
        give(25, vid=uid)
        with mock.patch.object(app, "llm_generate", return_value=("AI deep", {})):
            code, data, _ = self.req("POST", "/api/reading", {**BASE, "cardCount": 12, "jobId": JOB})
            self.assertEqual((code, data["ok"], data["jobId"]), (202, True, JOB))
            self.assertEqual(credits_of(uid), 5)
            for _ in range(200):
                code, data, headers = self.req("GET", f"/api/reading/job/{JOB}")
                if data.get("status") != "working":
                    break
                time.sleep(0.02)
        self.assertEqual((code, data["status"]), (200, "done"))
        self.assertEqual(headers.get("Cache-Control"), "no-store")
        self.assertEqual(data["result"]["reading"], "AI deep")
        self.assertEqual(data["result"]["account"], {"username": "job_tester"})
        self.assertEqual(data["balance"]["credits"], 5)
        self.assertEqual(self.req("POST", f"/api/reading/job/{JOB}/ack", {})[0], 200)
        self.assertEqual(self.req("GET", f"/api/reading/job/{JOB}")[1]["status"], "gone")
        self.assertEqual(self.req("GET", f"/api/reading/job/{'q' * 24}")[0], 404)
        self.assertEqual(credits_of(uid), 5)

    def test_http_402_and_old_sync_path_still_work(self):
        uid = self.signup()
        give(19, vid=uid)
        code, data, _ = self.req("POST", "/api/reading", {**BASE, "cardCount": 12, "jobId": JOB})
        self.assertEqual((code, data.get("code")), (402, "not_enough_credits"))
        self.assertEqual(credits_of(uid), 19)
        give(3, vid=uid)
        with mock.patch.object(app, "llm_generate", return_value=("AI", {})):
            code, data, _ = self.req("POST", "/api/reading", {**BASE, "cardCount": 3})  # no jobId: old behaviour
        self.assertEqual((code, data["balance"]["credits"]), (200, 2))


if __name__ == "__main__":
    unittest.main()
