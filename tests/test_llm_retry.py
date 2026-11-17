"""llm_generate retries transient failures (mocked urlopen, no network)."""
import io
import json
import os
import socket
import sys
import unittest
import urllib.error
from email.message import Message
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app  # noqa: E402
import tarot  # noqa: E402


class Resp:
    def __init__(self, text="บทอ่าน AI"):
        self.body = json.dumps({"choices": [{"message": {"content": text}}]}).encode()

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def http_error(code, retry_after=None):
    h = Message()
    if retry_after is not None:
        h["Retry-After"] = str(retry_after)
    return urllib.error.HTTPError("https://x/chat/completions", code, "err", h, io.BytesIO(b"{}"))


class Retry(unittest.TestCase):
    def run_with(self, outcomes):
        calls, sleeps, timeouts = [], [], []
        seq = list(outcomes)

        def fake_urlopen(req, timeout):
            calls.append(req)
            timeouts.append(timeout)
            o = seq.pop(0)
            if isinstance(o, BaseException):
                raise o
            return o

        cards = tarot.draw()
        err = io.StringIO()
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "sk-secret-test"}), \
                mock.patch.object(app.urllib.request, "urlopen", fake_urlopen), \
                mock.patch.object(app, "_sleep", sleeps.append), \
                mock.patch("sys.stderr", err):
            out = app.llm_generate("น้ำ", "love", "q", "th", cards=cards)
        self.assertNotIn("sk-secret-test", err.getvalue())
        return out, calls, sleeps, timeouts, err.getvalue()

    def test_success_first_try_no_sleep(self):
        out, calls, sleeps, _, _ = self.run_with([Resp()])
        self.assertEqual(out[0], "บทอ่าน AI")
        self.assertEqual((len(calls), sleeps), (1, []))

    def test_retries_each_transient_status_then_succeeds(self):
        for code in (429, 500, 502, 503, 504):
            out, calls, sleeps, _, log = self.run_with([http_error(code), Resp()])
            self.assertEqual(out[0], "บทอ่าน AI", code)
            self.assertEqual(len(calls), 2)
            self.assertEqual(len(sleeps), 1)
            self.assertIn(f"retrying", log)
            self.assertIn(f"HTTP {code}", log)

    def test_three_attempts_max_then_template(self):
        out, calls, sleeps, _, log = self.run_with([http_error(503)] * 3)
        self.assertIsNone(out)
        self.assertEqual(len(calls), 3)
        self.assertEqual(len(sleeps), 2)
        self.assertTrue(1.0 <= sleeps[0] <= 1.3, sleeps)
        self.assertTrue(2.5 <= sleeps[1] <= 3.25, sleeps)
        self.assertIn("LLM request failed (HTTP 503); using template generator.", log)

    def test_no_retry_on_client_errors(self):
        for code in (400, 401, 403, 404):
            out, calls, sleeps, _, _ = self.run_with([http_error(code), Resp()])
            self.assertIsNone(out)
            self.assertEqual((len(calls), sleeps), (1, []), code)

    def test_retry_after_respected_and_capped(self):
        _, _, sleeps, _, _ = self.run_with([http_error(429, retry_after=4), Resp()])
        self.assertEqual(sleeps, [4.0])
        _, _, sleeps, _, _ = self.run_with([http_error(429, retry_after=120), Resp()])
        self.assertEqual(sleeps, [app.LLM_RETRY_AFTER_CAP])
        _, _, sleeps, _, _ = self.run_with([http_error(429, retry_after="soon"), Resp()])
        self.assertTrue(1.0 <= sleeps[0] <= 1.3)

    def test_timeouts_and_network_errors_retry(self):
        out, calls, _, _, log = self.run_with([socket.timeout("t"), urllib.error.URLError("reset"), Resp()])
        self.assertEqual(out[0], "บทอ่าน AI")
        self.assertEqual(len(calls), 3)
        self.assertIn("timeout", log)

    def test_bad_json_not_retried(self):
        bad = Resp()
        bad.body = b"not json"
        out, calls, _, _, _ = self.run_with([bad, Resp()])
        self.assertIsNone(out)
        self.assertEqual(len(calls), 1)

    def test_worst_case_under_a_minute(self):
        clock = [0.0]

        def fake_urlopen(req, timeout):
            clock[0] += timeout  # each attempt burns its full timeout
            raise socket.timeout("t")

        def fake_sleep(s):
            clock[0] += s

        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "k"}), \
                mock.patch.object(app.urllib.request, "urlopen", fake_urlopen), \
                mock.patch.object(app, "_sleep", fake_sleep), \
                mock.patch.object(app, "_monotonic", lambda: clock[0]), \
                mock.patch("sys.stderr", io.StringIO()):
            self.assertIsNone(app.llm_generate("a", "love", "q", "th", cards=tarot.draw()))
        self.assertLessEqual(clock[0], 60)


if __name__ == "__main__":
    unittest.main()
