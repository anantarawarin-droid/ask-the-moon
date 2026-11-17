"""Automatic payment-slip verification through SlipOK (https://slipok.com).

Enabled only when SLIPOK_BRANCH_ID and SLIPOK_API_KEY are set. The key is
sent as a header and never logged. Slip images are forwarded to SlipOK and
not stored; only a short summary is kept on the order.
"""

from __future__ import annotations

import json
import os
import re
import secrets
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any

SLIPOK_URL = "https://api.slipok.com/api/line/apikey/"
# SlipOK sits behind Cloudflare, which rejects the default "Python-urllib" agent (403 / error 1010).
USER_AGENT = "AskTheMoon/1.0 (+https://ask-the-moon.onrender.com)"
TIMEOUT_SECONDS = 20
MAX_BYTES = 4 * 1024 * 1024
MAX_ATTEMPTS_PER_ORDER = 5
VISITOR_WINDOW_SECONDS = 600
MAX_UPLOADS_PER_VISITOR_WINDOW = 8

EXTENSIONS = {"image/jpeg": "slip.jpg", "image/png": "slip.png", "image/webp": "slip.webp"}


def config() -> tuple[str, str] | None:
    branch = os.environ.get("SLIPOK_BRANCH_ID", "").strip()
    key = os.environ.get("SLIPOK_API_KEY", "").strip()
    if not branch or not key:
        return None
    return branch, key


def enabled() -> bool:
    return config() is not None


def sniff_image(data: bytes) -> str | None:
    """Return the MIME type from the file's magic bytes, or None."""
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


# ---------------------------------------------------------------------------
# Rate limiting (in memory; resets on restart, the per-order cap is stored)
# ---------------------------------------------------------------------------
class VisitorLimiter:
    def __init__(self, limit: int = MAX_UPLOADS_PER_VISITOR_WINDOW, window: int = VISITOR_WINDOW_SECONDS):
        self.limit = limit
        self.window = window
        self._hits: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            hits = [t for t in self._hits.get(key, []) if now - t < self.window]
            if len(hits) >= self.limit:
                self._hits[key] = hits
                return False
            hits.append(now)
            self._hits[key] = hits
            if len(self._hits) > 5000:  # keep memory bounded
                for k in list(self._hits)[:1000]:
                    self._hits.pop(k, None)
            return True


LIMITER = VisitorLimiter()


# ---------------------------------------------------------------------------
# SlipOK call
# ---------------------------------------------------------------------------
def _multipart(fields: dict[str, str], file_bytes: bytes | None, filename: str, mime: str) -> tuple[bytes, str]:
    boundary = "----moon" + secrets.token_hex(12)
    out = bytearray()
    for name, value in fields.items():
        out += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n").encode()
    if file_bytes is not None:
        out += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"files\"; filename=\"{filename}\"\r\n"
                f"Content-Type: {mime}\r\n\r\n").encode()
        out += file_bytes + b"\r\n"
    out += f"--{boundary}--\r\n".encode()
    return bytes(out), f"multipart/form-data; boundary={boundary}"


_QR_OK = re.compile(r"^[\x20-\x7e]{10,512}$")


def clean_qr(raw: Any) -> str | None:
    """QR text the browser read from the slip (printable ASCII only), or None."""
    text = urllib.parse.unquote(str(raw or "")).strip()
    return text if _QR_OK.match(text) else None


def slipok_request(image: bytes, mime: str, amount: int | None = None, qr: str | None = None,
                   log: bool = True, qr_form: bool = False) -> tuple[int, dict[str, Any]]:
    """One HTTP call to SlipOK. Returns (status, json). Raises on network errors/timeouts.

    With ``qr`` the QR text is sent as ``data`` (SlipOK's own field for it) instead of the image,
    as JSON or (``qr_form``) as a form field. ``amount`` is only sent when given: we compare the
    amount ourselves, and SlipOK's examples leave it out.
    """
    cfg = config()
    if cfg is None:
        raise RuntimeError("SlipOK is not configured")
    branch, key = cfg
    fields: dict[str, Any] = {}
    if amount is not None:
        fields["amount"] = amount
    if log:
        fields["log"] = True
    if qr and not qr_form:
        body = json.dumps({"data": qr, **fields}).encode()
        ctype = "application/json"
    else:
        form = {k: ("true" if v is True else str(v)) for k, v in fields.items()}
        if qr:
            body, ctype = _multipart({"data": qr, **form}, None, "", "")
        else:
            body, ctype = _multipart(form, image, EXTENSIONS[mime], mime)
    req = urllib.request.Request(
        SLIPOK_URL + urllib.request.quote(branch, safe=""),
        data=body,
        method="POST",
        headers={"x-authorization": key, "Content-Type": ctype, "Accept": "application/json",
                 "User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            status, raw = resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        status, raw = exc.code, exc.read()
    try:
        payload = json.loads(raw.decode("utf-8") or "{}")
    except ValueError:
        payload = {}
    return status, payload if isinstance(payload, dict) else {}


SETUP_PROBLEMS = {
    1001: "branch ID not found (check SLIPOK_BRANCH_ID)",
    1002: "API key rejected (check SLIPOK_API_KEY)",
    1003: "SlipOK package expired — renew it in SlipOK",
    1004: "SlipOK quota used up — top up / renew the package",
}
# Not the customer's fault, or nothing was really checked: these uploads don't use up an attempt.
UNCOUNTED_CODES = {"1000", "1005", "1006", "1007", "1008", "1009", "1010", "1001", "1002", "1003", "1004",
                   "timeout", "network", "URLError", "OSError", "ConnectionError", "RemoteDisconnected"}
# SlipOK could not find a usable slip in the uploaded picture.
UNREADABLE_CODES = {1000, 1005, 1006, 1007, 1008}


def _code(payload: dict[str, Any]) -> int | None:
    try:
        return int(payload.get("code"))
    except (TypeError, ValueError):
        return None


# SlipOK answers 1000 ("put in correct data") when it rejects the request itself.
REQUEST_REJECTED = 1000


def _log_attempt(label: str, result: dict[str, Any]) -> None:
    """Diagnostics only: HTTP status and SlipOK code/message. Never the key, branch, or slip data."""
    p = result.get("payload") or {}
    print(f"SlipOK try {label}: HTTP {result.get('status')} code {p.get('code')} "
          f"msg {str(p.get('message') or '')[:80]!r}" + (f" error {result['error']}" if result.get("error") else ""),
          flush=True)


def check_slip(image: bytes, mime: str, amount: int, qr: str | None = None) -> dict[str, Any]:
    """Ask SlipOK about the slip. Never raises.

    1. the image (SlipOK reads the QR itself);
    2. if SlipOK can't read it and the browser already read the slip's QR: that QR text (JSON),
    3. ... then the QR text as a form field;
    4. if SlipOK still rejects the request itself (1000): the image without ``log``. A pass there
       skips SlipOK's receiver/duplicate checks, so it only goes to the admin for review.
    The amount is checked locally (``classify``), so it is not sent.

    Returns {"status", "payload", "retried", "error", "via", ...}.
    """
    plan: list[tuple[str, dict[str, Any]]] = [("image", {})]
    result: dict[str, Any] = {}
    first: int | None = None
    tried: list[str] = []
    while plan:
        via, kw = plan.pop(0)
        result = _check_once(image, mime, None, **kw)
        result["via"] = via
        tried.append(via)
        _log_attempt(via, result)
        if result.get("status") is None:
            break
        code = _code(result.get("payload") or {})
        if first is None:
            first = code
        if via == "image" and code in (1000, 1006, 1007) and qr:
            plan = [("qr", {"qr": qr}), ("qr-form", {"qr": qr, "qr_form": True})]
            if code == REQUEST_REJECTED:
                plan.append(("image-nolog", {"log": False}))
            continue
        if via == "image" and code == REQUEST_REJECTED:
            plan = [("image-nolog", {"log": False})]
            continue
        if via == "qr" and code == REQUEST_REJECTED:
            continue  # try the next way
        if via == "qr-form" and code == REQUEST_REJECTED:
            continue
        break
    if len(tried) > 1:
        result["firstCode"] = first
        result["tried"] = tried
    if result.get("via") == "image-nolog":
        result["nolog"] = True
    return result


def _check_once(image: bytes, mime: str, amount: int | None, qr: str | None = None, **kw: Any) -> dict[str, Any]:
    """One SlipOK check with one retry on timeouts, network errors, and 5xx."""
    result: dict[str, Any] = {"status": None, "payload": {}, "retried": False, "error": None}
    for attempt in (1, 2):
        try:
            status, payload = slipok_request(image, mime, amount, qr, **kw)
            result.update(status=status, payload=payload, error=None)
            if status >= 500 and attempt == 1:
                result["retried"] = True
                time.sleep(1.0)
                continue
            return result
        except (TimeoutError, urllib.error.URLError, OSError) as exc:
            reason = getattr(exc, "reason", exc)
            result["error"] = "timeout" if isinstance(reason, TimeoutError) or isinstance(exc, TimeoutError) else type(exc).__name__
            if attempt == 1:
                result["retried"] = True
                time.sleep(1.0)
                continue
            return result
    return result


# ---------------------------------------------------------------------------
# Interpreting the answer
# ---------------------------------------------------------------------------
@dataclass
class Outcome:
    kind: str  # "success" | "failed" | "review"
    code: str
    note: str  # short admin-facing note (no secrets)
    th: str
    en: str
    summary: dict[str, Any] = field(default_factory=dict)
    trans_ref: str | None = None


def summarize(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    sender = data.get("sender") or {}
    receiver = data.get("receiver") or {}
    keep = {
        "transRef": data.get("transRef"),
        "amount": data.get("amount"),
        "transDate": data.get("transDate"),
        "transTime": data.get("transTime"),
        "sendingBank": data.get("sendingBank"),
        "receivingBank": data.get("receivingBank"),
        "sender": (sender.get("displayName") or sender.get("name")) if isinstance(sender, dict) else None,
        "receiver": (receiver.get("displayName") or receiver.get("name")) if isinstance(receiver, dict) else None,
    }
    return {k: (str(v)[:60] if v is not None else None) for k, v in keep.items() if v not in (None, "")}


def _amount_matches(value: Any, price: int) -> bool:
    try:
        return abs(float(value) - float(price)) < 0.005
    except (TypeError, ValueError):
        return False


MSG = {
    "success": ("ตรวจสลิปผ่านแล้ว! เติมคำถามให้เรียบร้อย ✨", "Slip verified! Your questions have been added ✨"),
    "amount": ("ยอดในสลิปไม่ตรงกับคำสั่งซื้อ กรุณาโอนให้ตรงยอด หรืออัปโหลดสลิปที่ถูกต้อง",
               "The slip amount doesn't match this order. Please pay the exact amount or upload the right slip."),
    "receiver": ("บัญชีผู้รับในสลิปไม่ใช่บัญชีของถามจันทร์ กรุณาตรวจสอบการโอนอีกครั้ง",
                 "This slip was paid to a different account. Please check your transfer."),
    "duplicate": ("สลิปนี้เคยใช้ไปแล้ว ไม่สามารถใช้ซ้ำได้", "This slip has already been used and can't be used again."),
    "not_slip": ("ระบบอ่านสลิปจากรูปนี้ไม่ได้ กรุณาอัปโหลดรูปสลิปเต็มใบจากแอปธนาคาร (บันทึกรูปสลิปหรือแคปหน้าจอ) "
                 "ให้เห็น QR มุมสลิปชัด ๆ ไม่ครอป ไม่ถ่ายจากจออื่น · ครั้งนี้ไม่นับจำนวนครั้ง",
                 "We couldn't read a slip in this picture. Please upload the full slip from your banking app "
                 "(saved slip image or a screenshot) with its QR code clearly visible, not cropped or photographed "
                 "from another screen. This try doesn't count."),
    "review": ("กำลังตรวจสอบเพิ่มเติม เครดิตจะเข้าอัตโนมัติเมื่อผ่าน",
               "We're checking this further. Credits are added automatically once it passes."),
    "delay": ("ธนาคารนี้ต้องรอสักครู่ก่อนตรวจสลิปได้ ลองอัปโหลดอีกครั้งในอีกไม่กี่นาที หรือรอแอดมินตรวจให้",
              "This bank needs a few minutes before slips can be checked. Try again in a few minutes, or wait for the admin to check it."),
}


def classify(check: dict[str, Any], price: int, prior_review: bool = False) -> Outcome:
    status = check.get("status")
    payload = check.get("payload") or {}
    data = payload.get("data")
    summary = summarize(data)

    if status is None:
        err = check.get("error") or "network"
        return Outcome("review", err, f"SlipOK unreachable ({err}); check manually", *MSG["review"])

    if status == 200 and payload.get("success") and isinstance(data, dict) and data.get("success") is not False:
        ref = str(data.get("transRef") or "").strip()
        if not ref:
            return Outcome("review", "no_ref", "SlipOK OK but no transRef; check manually", *MSG["review"], summary=summary)
        if not _amount_matches(data.get("amount"), price):
            return Outcome("failed", "amount_local", f"slip amount {data.get('amount')} ≠ order {price}",
                           *MSG["amount"], summary=summary, trans_ref=ref)
        if check.get("nolog"):
            return Outcome("review", "nolog", "SlipOK read the slip (amount OK) but rejected the shop check (log); "
                           "confirm the money arrived", *MSG["review"], summary=summary, trans_ref=None)
        return Outcome("success", "ok", "verified by SlipOK", *MSG["success"], summary=summary, trans_ref=ref)

    code = payload.get("code")
    try:
        code_i = int(code)
    except (TypeError, ValueError):
        code_i = None

    if code_i == 1013:
        return Outcome("failed", "1013", "SlipOK 1013 wrong amount", *MSG["amount"], summary=summary)
    if code_i == 1014:
        return Outcome("failed", "1014", "SlipOK 1014 wrong receiver", *MSG["receiver"], summary=summary)
    if code_i == 1012:
        if (check.get("retried") or prior_review) and _amount_matches(summary.get("amount"), price):
            # Likely our own earlier call that SlipOK already logged (a timed-out
            # first try, or an earlier "check manually" upload): let the admin decide.
            return Outcome("review", "1012", "SlipOK 1012 repeated slip; amount matches — confirm it isn't reused",
                           *MSG["review"], summary=summary, trans_ref=None)
        return Outcome("failed", "1012", "SlipOK 1012 repeated slip", *MSG["duplicate"], summary=summary)
    if code_i in UNREADABLE_CODES:
        msg = str(payload.get("message") or "")[:80]
        return Outcome("failed", str(code_i), f"SlipOK {code_i} no readable slip/QR in the picture ({msg}); "
                       "customer asked to re-upload", *MSG["not_slip"], summary=summary)
    if code_i == 1010:
        delay = (data or {}).get("delay") if isinstance(data, dict) else None
        return Outcome("review", "1010", f"SlipOK 1010 bank delay{f' ({delay} min)' if delay else ''}; retry or check manually",
                       *MSG["delay"], summary=summary)
    if code_i in (1009, 1011):
        return Outcome("review", str(code_i), f"SlipOK {code_i} bank data not available yet; check manually",
                       *MSG["review"], summary=summary)
    if code_i in SETUP_PROBLEMS:
        print(f"SlipOK setup problem: code {code_i} ({SETUP_PROBLEMS[code_i]})", file=sys.stderr, flush=True)
        return Outcome("review", str(code_i), f"SlipOK {code_i}: {SETUP_PROBLEMS[code_i]}; check manually",
                       *MSG["review"], summary=summary)
    return Outcome("review", str(code_i or status), f"SlipOK HTTP {status} code {code_i}; check manually",
                   *MSG["review"], summary=summary)
