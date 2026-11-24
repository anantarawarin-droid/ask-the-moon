"""Anonymous visitor notes: validation and an in-memory rate limit.

Stored fields are only the message, timestamp, language, and an optional
coarse page tag. IP addresses are used for the rate limit in process memory
and are never written down.
"""

from __future__ import annotations

import secrets
from typing import Any

import credits as billing
from slips import VisitorLimiter

MAX_LEN = 500
PAGE_TAGS = frozenset({"home", "reading", "pricing", "faq"})
# A few notes per IP in a short window; hits vanish on restart.
BY_IP = VisitorLimiter(limit=3, window=600)


def new_id() -> str:
    return "fb_" + secrets.token_urlsafe(8)


def honeypot_filled(body: dict[str, Any]) -> bool:
    for key in ("website", "company", "url"):
        if str(body.get(key) or "").strip():
            return True
    return False


def normalize(body: dict[str, Any]) -> dict[str, str]:
    message = str(body.get("message") or "").strip()
    if not message:
        lang = _lang(body)
        raise billing.PaymentError(
            "Please write a short message first." if lang == "en" else "พิมพ์ข้อความก่อนส่งนะ",
            400,
            "empty",
        )
    if len(message) > MAX_LEN:
        message = message[:MAX_LEN]
    page = str(body.get("page") or "").strip().lower()
    if page not in PAGE_TAGS:
        page = "home"
    return {"message": message, "lang": _lang(body), "page": page}


def _lang(body: dict[str, Any]) -> str:
    return "en" if str(body.get("lang") or "").lower().startswith("en") else "th"


def public_item(item: dict[str, Any]) -> dict[str, Any]:
    """Only the fields the owner should see — never an IP or account id."""
    return {
        "id": item["id"],
        "message": item["message"],
        "lang": item.get("lang") or "th",
        "page": item.get("page") or "home",
        "createdAt": item.get("createdAt"),
    }
