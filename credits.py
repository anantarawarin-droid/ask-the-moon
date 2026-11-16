"""Pricing, question credits, PromptPay orders, and storage for ถามจันทร์.

Everything about money lives here so app.py stays focused on readings.
Standard library only.

The storage is a small JSON file guarded by a lock and written atomically.
To move to a real database later, implement the same methods as JsonStore
(get_balance, reserve_credit, refund_credit, create_order, ...) and pass
that object to CreditService.
"""

from __future__ import annotations

import hmac
import json
import os
import re
import secrets
import tempfile
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any, Iterator

# ---------------------------------------------------------------------------
# Pricing — the single source of truth. Do not change without the owner.
# (price in THB, total questions). Bonus = total - price / 15.
# ---------------------------------------------------------------------------
BASE_PRICE = 15
MAX_AMOUNT = 150
PACKAGE_TABLE: tuple[tuple[int, int], ...] = (
    (15, 1),
    (30, 2),
    (45, 3),
    (60, 4),
    (75, 5),
    (90, 7),
    (105, 8),
    (120, 10),
    (135, 12),
    (150, 15),
)
BEST_VALUE_PRICE = 150


def _money(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def build_packages() -> list[dict[str, Any]]:
    packages = []
    for price, questions in PACKAGE_TABLE:
        if price % BASE_PRICE or price > MAX_AMOUNT:
            raise ValueError(f"Invalid package price {price}")
        base = price // BASE_PRICE
        bonus = questions - base
        if bonus < 0:
            raise ValueError(f"Package {price} has fewer questions than its base")
        avg = Decimal(price) / Decimal(questions)
        packages.append(
            {
                "price": price,
                "questions": questions,
                "baseQuestions": base,
                "bonus": bonus,
                "perQuestion": _money(avg),
                "worth": questions * BASE_PRICE,
                "savings": questions * BASE_PRICE - price,
                "savingsPercent": int(
                    ((Decimal(questions * BASE_PRICE - price) / Decimal(questions * BASE_PRICE)) * 100)
                    .quantize(Decimal("1"), rounding=ROUND_HALF_UP)
                ),
                "bestValue": price == BEST_VALUE_PRICE,
            }
        )
    return packages


PACKAGES = build_packages()
PACKAGES_BY_PRICE = {p["price"]: p for p in PACKAGES}


def package_for_amount(amount: Any) -> dict[str, Any]:
    """Return the package for an exact THB amount, or raise ValueError."""
    if isinstance(amount, bool):
        raise ValueError("Invalid package amount.")
    if isinstance(amount, str) and re.fullmatch(r"\d{1,4}", amount.strip()):
        amount = int(amount.strip())
    if isinstance(amount, float) and amount.is_integer():
        amount = int(amount)
    if not isinstance(amount, int) or amount not in PACKAGES_BY_PRICE:
        raise ValueError("Invalid package amount.")
    return PACKAGES_BY_PRICE[amount]


# ---------------------------------------------------------------------------
# PromptPay (EMVCo merchant-presented QR, Thai BOT spec)
# ---------------------------------------------------------------------------
PROMPTPAY_AID = "A000000677010111"


def crc16_ccitt(data: str) -> str:
    """CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF), uppercase hex."""
    crc = 0xFFFF
    for byte in data.encode("ascii"):
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else (crc << 1)
            crc &= 0xFFFF
    return f"{crc:04X}"


def _tlv(tag: str, value: str) -> str:
    return f"{tag}{len(value):02d}{value}"


def normalize_promptpay_id(raw: str | None) -> tuple[str, str] | None:
    """Return (sub-tag, formatted target) or None if the id is not usable."""
    if not raw:
        return None
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 10 and digits.startswith("0"):  # mobile phone
        return "01", ("0066" + digits[1:]).rjust(13, "0")
    if len(digits) == 13:  # national id / tax id
        return "02", digits
    if len(digits) == 15:  # e-wallet id
        return "03", digits
    return None


def promptpay_payload(promptpay_id: str, amount: int | float | None = None) -> str:
    target = normalize_promptpay_id(promptpay_id)
    if target is None:
        raise ValueError("PROMPTPAY_ID must be a 10-digit phone, 13-digit ID, or 15-digit e-wallet.")
    sub_tag, value = target
    merchant = _tlv("00", PROMPTPAY_AID) + _tlv(sub_tag, value)
    parts = [
        _tlv("00", "01"),
        _tlv("01", "12" if amount else "11"),
        _tlv("29", merchant),
        _tlv("58", "TH"),
        _tlv("53", "764"),
    ]
    if amount:
        parts.append(_tlv("54", f"{Decimal(str(amount)).quantize(Decimal('0.01'))}"))
    body = "".join(parts) + "6304"
    return body + crc16_ccitt(body)


def promptpay_id_from_env() -> str | None:
    raw = os.environ.get("PROMPTPAY_ID", "").strip()
    return raw if normalize_promptpay_id(raw) else None


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------
VISITOR_RE = re.compile(r"^[A-Za-z0-9_-]{16,64}$")
ORDER_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
MAX_PENDING_PER_VISITOR = 5
MAX_PENDING_TOTAL = 2000


class PaymentError(Exception):
    def __init__(self, message: str, status: int = 400, code: str = "error"):
        super().__init__(message)
        self.status = status
        self.code = code


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def valid_visitor_id(visitor_id: Any) -> bool:
    return isinstance(visitor_id, str) and bool(VISITOR_RE.match(visitor_id))


class JsonStore:
    """Tiny JSON-file store. One process, many threads."""

    def __init__(self, data_dir: str | os.PathLike[str]):
        self.dir = Path(data_dir)
        self.path = self.dir / "credits.json"
        self._lock = threading.RLock()
        self._data = self._load()

    def _load(self) -> dict[str, Any]:
        try:
            with open(self.path, encoding="utf-8") as fh:
                data = json.load(fh)
        except FileNotFoundError:
            data = {}
        data.setdefault("visitors", {})
        data.setdefault("orders", {})
        return data

    def _save(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".credits-", suffix=".json", dir=self.dir)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh, ensure_ascii=False, indent=1)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, self.path)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    @contextmanager
    def transaction(self) -> Iterator[dict[str, Any]]:
        """Hold the lock, yield the data, save on success, roll back on error."""
        with self._lock:
            snapshot = json.loads(json.dumps(self._data))
            try:
                yield self._data
                self._save()
            except BaseException:
                self._data = snapshot
                raise

    @contextmanager
    def read(self) -> Iterator[dict[str, Any]]:
        with self._lock:
            yield self._data


class CreditService:
    def __init__(self, store: JsonStore):
        self.store = store

    # -- visitors ---------------------------------------------------------
    @staticmethod
    def _visitor(data: dict[str, Any], visitor_id: str) -> dict[str, Any]:
        v = data["visitors"].get(visitor_id)
        if v is None:
            v = {"credits": 0, "freeUsed": False, "createdAt": _now()}
            data["visitors"][visitor_id] = v
        return v

    def balance(self, visitor_id: str) -> dict[str, Any]:
        with self.store.read() as data:
            v = data["visitors"].get(visitor_id) or {"credits": 0, "freeUsed": False}
            return {"credits": int(v["credits"]), "freeAvailable": not v["freeUsed"]}

    def reserve_reading(self, visitor_id: str) -> str:
        """Atomically take 1 credit (or the one free preview). Returns 'paid' or 'free'."""
        with self.store.transaction() as data:
            v = self._visitor(data, visitor_id)
            if v["credits"] > 0:
                v["credits"] -= 1
                return "paid"
            if not v["freeUsed"]:
                v["freeUsed"] = True
                return "free"
            raise PaymentError("No question credits left.", status=402, code="no_credits")

    def release_reading(self, visitor_id: str, kind: str) -> None:
        """Give back a reservation when the reading failed or was not AI-written."""
        with self.store.transaction() as data:
            v = self._visitor(data, visitor_id)
            if kind == "paid":
                v["credits"] += 1
            elif kind == "free":
                v["freeUsed"] = False

    # -- orders -----------------------------------------------------------
    def create_order(self, visitor_id: str, amount: Any) -> dict[str, Any]:
        pkg = package_for_amount(amount)
        with self.store.transaction() as data:
            pending = [o for o in data["orders"].values() if o["status"] == "pending"]
            mine = [o for o in pending if o["visitor"] == visitor_id]
            for o in mine:  # reuse an identical pending order instead of piling up
                if o["price"] == pkg["price"]:
                    return dict(o)
            if len(mine) >= MAX_PENDING_PER_VISITOR or len(pending) >= MAX_PENDING_TOTAL:
                raise PaymentError("Too many pending orders. Please wait for approval.", 429, "too_many")
            code = self._new_code(data)
            order = {
                "code": code,
                "visitor": visitor_id,
                "price": pkg["price"],
                "questions": pkg["questions"],
                "bonus": pkg["bonus"],
                "status": "pending",
                "createdAt": _now(),
                "decidedAt": None,
            }
            data["orders"][code] = order
            return dict(order)

    @staticmethod
    def _new_code(data: dict[str, Any]) -> str:
        while True:
            code = "M" + "".join(secrets.choice(ORDER_ALPHABET) for _ in range(5))
            if code not in data["orders"]:
                return code

    def visitor_orders(self, visitor_id: str, limit: int = 10) -> list[dict[str, Any]]:
        with self.store.read() as data:
            mine = [dict(o) for o in data["orders"].values() if o["visitor"] == visitor_id]
        mine.sort(key=lambda o: o["createdAt"], reverse=True)
        return mine[:limit]

    def list_orders(self, status: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        with self.store.read() as data:
            orders = [dict(o) for o in data["orders"].values() if status in (None, o["status"])]
            for o in orders:
                v = data["visitors"].get(o["visitor"]) or {"credits": 0}
                o["visitorCredits"] = v["credits"]
        orders.sort(key=lambda o: o["createdAt"], reverse=True)
        return orders[:limit]

    def approve(self, code: str) -> dict[str, Any]:
        """Approve a pending order. Credits are added exactly once."""
        with self.store.transaction() as data:
            order = data["orders"].get(str(code).upper())
            if order is None:
                raise PaymentError("Order not found.", 404, "not_found")
            if order["status"] == "approved":
                return {"order": dict(order), "alreadyApproved": True,
                        "credits": self._visitor(data, order["visitor"])["credits"]}
            if order["status"] != "pending":
                raise PaymentError("Only pending orders can be approved.", 409, "not_pending")
            v = self._visitor(data, order["visitor"])
            v["credits"] += int(order["questions"])
            order["status"] = "approved"
            order["decidedAt"] = _now()
            return {"order": dict(order), "alreadyApproved": False, "credits": v["credits"]}

    def reject(self, code: str) -> dict[str, Any]:
        with self.store.transaction() as data:
            order = data["orders"].get(str(code).upper())
            if order is None:
                raise PaymentError("Order not found.", 404, "not_found")
            if order["status"] == "rejected":
                return {"order": dict(order)}
            if order["status"] != "pending":
                raise PaymentError("Only pending orders can be rejected.", 409, "not_pending")
            order["status"] = "rejected"
            order["decidedAt"] = _now()
            return {"order": dict(order)}


def public_order(order: dict[str, Any]) -> dict[str, Any]:
    return {k: order[k] for k in ("code", "price", "questions", "bonus", "status", "createdAt", "decidedAt")}


def admin_token_ok(given: str | None) -> bool | None:
    """True/False for a match; None when ADMIN_TOKEN is not configured."""
    expected = os.environ.get("ADMIN_TOKEN", "")
    if not expected:
        return None
    return hmac.compare_digest((given or "").encode("utf-8"), expected.encode("utf-8"))
