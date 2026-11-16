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
        data.setdefault("users", {})
        data.setdefault("sessions", {})
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
            self.usernames_for(data, orders)
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


    # -- accounts ---------------------------------------------------------------
    def create_user(self, user_id: str, username: str, password_record: str) -> dict[str, Any]:
        key = username.lower()
        with self.store.transaction() as data:
            if any(u["usernameKey"] == key for u in data["users"].values()):
                raise PaymentError("That username is taken.", 409, "username_taken")
            user = {"id": user_id, "username": username, "usernameKey": key,
                    "password": password_record, "createdAt": _now()}
            data["users"][user_id] = user
            self._visitor(data, user_id)
            return {"id": user_id, "username": username}

    def find_user(self, username: str) -> dict[str, Any] | None:
        key = username.strip().lower()
        with self.store.read() as data:
            for u in data["users"].values():
                if u["usernameKey"] == key:
                    return dict(u)
        return None

    def set_password(self, user_id: str, password_record: str) -> None:
        with self.store.transaction() as data:
            data["users"][user_id]["password"] = password_record
            data["users"][user_id]["passwordChangedAt"] = _now()

    def create_session(self, user_id: str, token_hash: str, expires_at: datetime) -> None:
        with self.store.transaction() as data:
            now = datetime.now(timezone.utc).isoformat()
            for k in [k for k, v in data["sessions"].items() if v["expiresAt"] < now]:
                del data["sessions"][k]
            data["sessions"][token_hash] = {"userId": user_id, "createdAt": _now(),
                                            "expiresAt": expires_at.astimezone(timezone.utc).isoformat()}

    def session_user(self, token_hash: str) -> dict[str, Any] | None:
        with self.store.read() as data:
            sess = data["sessions"].get(token_hash)
            if not sess or sess["expiresAt"] <= datetime.now(timezone.utc).isoformat():
                return None
            u = data["users"].get(sess["userId"])
            return {"id": u["id"], "username": u["username"]} if u else None

    def delete_session(self, token_hash: str) -> None:
        with self.store.transaction() as data:
            data["sessions"].pop(token_hash, None)

    def delete_user_sessions(self, user_id: str) -> None:
        with self.store.transaction() as data:
            for k in [k for k, v in data["sessions"].items() if v["userId"] == user_id]:
                del data["sessions"][k]

    def merge_visitor(self, visitor_id: str, account_id: str) -> dict[str, Any]:
        """Move an anonymous visitor's credits, free-question use, and pending orders
        into the account. Safe to call any number of times."""
        with self.store.transaction() as data:
            wallet = self._visitor(data, account_id)
            moved, orders = 0, 0
            v = self._visitor(data, visitor_id) if visitor_id and visitor_id != account_id else None
            if v is not None:
                moved = int(v["credits"])
                wallet["credits"] += moved
                v["credits"] = 0
                if v["freeUsed"]:
                    wallet["freeUsed"] = True
                v["freeUsed"] = True  # the free question now lives with the account
                v["mergedInto"] = account_id
            for o in data["orders"].values():
                if visitor_id and o["visitor"] == visitor_id and o["status"] == "pending":
                    o["visitor"] = account_id
                    orders += 1
            return {"movedCredits": moved, "movedOrders": orders}

    def usernames_for(self, data: dict[str, Any], orders: list[dict[str, Any]]) -> None:
        for o in orders:
            u = data["users"].get(o["visitor"])
            o["username"] = u["username"] if u else None

    # -- slips ----------------------------------------------------------------
    def begin_slip_check(self, code: str, visitor_id: str, max_attempts: int) -> dict[str, Any]:
        with self.store.transaction() as data:
            order = data["orders"].get(str(code).upper())
            if order is None or order["visitor"] != visitor_id:
                raise PaymentError("Order not found.", 404, "not_found")
            if order["status"] == "approved":
                return dict(order)
            if order["status"] != "pending":
                raise PaymentError("This order is closed. Please create a new one.", 409, "not_pending")
            if int(order.get("slipAttempts") or 0) >= max_attempts:
                raise PaymentError("Too many slip uploads for this order.", 429, "too_many_slips")
            order["slipAttempts"] = int(order.get("slipAttempts") or 0) + 1
            return dict(order)

    def set_slip_result(self, code: str, status: str, note: str, summary: dict[str, Any]) -> dict[str, Any]:
        with self.store.transaction() as data:
            order = data["orders"][str(code).upper()]
            if order["status"] == "pending":
                order["slipStatus"] = status
                order["slipNote"] = note[:200]
                order["slipSummary"] = summary
                order["slipCheckedAt"] = _now()
            return dict(order)

    def trans_ref_used(self, trans_ref: str, except_code: str | None = None) -> bool:
        with self.store.read() as data:
            return any(o.get("slipTransRef") == trans_ref and o["code"] != except_code for o in data["orders"].values())

    def approve_with_slip(self, code: str, trans_ref: str, summary: dict[str, Any]) -> dict[str, Any]:
        """Atomically: refuse a transRef used by another order, store it, approve once."""
        with self.store.transaction() as data:
            order = data["orders"].get(str(code).upper())
            if order is None:
                raise PaymentError("Order not found.", 404, "not_found")
            for other in data["orders"].values():
                if other.get("slipTransRef") == trans_ref and other["code"] != order["code"]:
                    raise PaymentError("This slip was already used.", 409, "duplicate_slip")
            if order["status"] == "approved":
                if not order.get("slipTransRef"):
                    order["slipTransRef"] = trans_ref
                v = self._visitor(data, order["visitor"])
                return {"order": dict(order), "alreadyApproved": True, "credits": v["credits"]}
            if order["status"] != "pending":
                raise PaymentError("Only pending orders can be approved.", 409, "not_pending")
            v = self._visitor(data, order["visitor"])
            v["credits"] += int(order["questions"])
            order.update(status="approved", decidedAt=_now(), slipTransRef=trans_ref, slipStatus="verified",
                         slipNote="verified by SlipOK", slipSummary=summary, slipCheckedAt=_now())
            return {"order": dict(order), "alreadyApproved": False, "credits": v["credits"]}


def public_order(order: dict[str, Any]) -> dict[str, Any]:
    out = {k: order[k] for k in ("code", "price", "questions", "bonus", "status", "createdAt", "decidedAt")}
    out["slipStatus"] = order.get("slipStatus")
    return out


def admin_token_ok(given: str | None) -> bool | None:
    """True/False for a match; None when ADMIN_TOKEN is not configured."""
    expected = os.environ.get("ADMIN_TOKEN", "")
    if not expected:
        return None
    return hmac.compare_digest((given or "").encode("utf-8"), expected.encode("utf-8"))


# Backwards-compatible name: the JSON implementation.
JsonCreditService = CreditService


# ---------------------------------------------------------------------------
# Postgres store (used when DATABASE_URL is set)
# ---------------------------------------------------------------------------
_VENDOR = Path(__file__).resolve().parent / "vendor"


def _import_pg8000():
    try:
        import pg8000.dbapi  # type: ignore
    except ImportError:
        import sys

        if str(_VENDOR) not in sys.path:
            sys.path.append(str(_VENDOR))  # pure-Python copy shipped in the repo
        import pg8000.dbapi  # type: ignore
    _allow_server_scram_iterations()
    return pg8000.dbapi


def _allow_server_scram_iterations() -> None:
    """Accept whatever SCRAM iteration count the server chose, like libpq/psql.

    scramp rejects servers that use fewer than 4096 iterations, and some
    hosted Postgres roles (e.g. on Neon) are set up with fewer, which made the
    login fail with "The value must not be < 4096". The count is the server's
    own choice for its stored verifier, so the client accepting it does not
    weaken the TLS-protected connection.
    """
    try:
        import scramp.core as scramp_core  # type: ignore
    except ImportError:
        return
    cls = getattr(scramp_core, "IterationCount", None)
    if cls is not None and getattr(cls, "MIN_ITERATION_COUNT", 1) > 1:
        cls.MIN_ITERATION_COUNT = 1


class DatabaseConfigError(Exception):
    """Raised with a message that never contains the URL or password."""


def normalize_database_url(raw: str) -> str:
    """Forgive common copy-paste wrappers, e.g. Neon's  psql 'postgresql://...'  snippet."""
    url = (raw or "").strip()
    for _ in range(3):
        before = url
        if url.upper().startswith("DATABASE_URL="):
            url = url[len("DATABASE_URL="):].strip()
        if url.lower().startswith("psql "):
            url = url[5:].strip()
        if len(url) >= 2 and url[0] == url[-1] and url[0] in "'\"":
            url = url[1:-1].strip()
        if url == before:
            break
    if not url.lower().startswith(("postgresql://", "postgres://")):
        # Still wrapped in other text (a label, a command, an env line...):
        # take the first postgres URL out of it.
        m = re.search(r"postgres(?:ql)?://[^\s'\"]+", url, flags=re.IGNORECASE)
        if m:
            NORMALIZE_NOTES.append(
                f"DATABASE_URL had {m.start()} extra characters before the URL"
                f" and {len(url) - m.end()} after it; used only the postgresql:// part."
            )
            url = m.group(0)
    return url


NORMALIZE_NOTES: list[str] = []


def describe_bad_database_url(raw: str) -> str:
    """Explain why a value is not a postgres URL without echoing it."""
    v = (raw or "").strip()
    low = v.lower()
    if not v:
        return "DATABASE_URL is empty."
    if low.startswith("jdbc:"):
        return "DATABASE_URL looks like a JDBC URL (starts with jdbc:); use the postgresql:// form."
    if low.startswith(("host=", "dbname=", "user=")):
        return "DATABASE_URL looks like a key=value connection string, not a postgresql:// URL."
    if "postgresql://" in low or "postgres://" in low:
        return "DATABASE_URL has extra text before postgresql:// (e.g. a command or label); paste only the URL."
    if "://" in v:
        return "DATABASE_URL uses a different scheme; it must start with postgresql:// or postgres://."
    return f"DATABASE_URL is not a URL (no postgresql:// prefix; value is {len(v)} characters long)."


def parse_database_url(url: str) -> dict[str, Any]:
    from urllib.parse import parse_qs, unquote, urlsplit

    raw = url
    url = normalize_database_url(url)
    try:
        parts = urlsplit(url)
    except ValueError as exc:
        raise DatabaseConfigError("DATABASE_URL could not be parsed.") from exc
    if parts.scheme not in ("postgres", "postgresql"):
        raise DatabaseConfigError(describe_bad_database_url(raw))
    try:
        port = parts.port or 5432
    except ValueError as exc:
        raise DatabaseConfigError("DATABASE_URL has an invalid port.") from exc
    if not parts.hostname:
        raise DatabaseConfigError("DATABASE_URL has no host.")
    if not parts.username:
        raise DatabaseConfigError("DATABASE_URL has no user name.")
    database = unquote(parts.path.lstrip("/")) or "postgres"
    query = {k: v[-1] for k, v in parse_qs(parts.query).items()}
    sslmode = query.get("sslmode", "require")
    if sslmode == "prefer":
        sslmode = "require"
    if sslmode not in ("disable", "require", "verify-ca", "verify-full", "prefer"):
        raise DatabaseConfigError("DATABASE_URL has an unsupported sslmode.")
    return {
        "host": parts.hostname,
        "port": port,
        "user": unquote(parts.username),
        "password": unquote(parts.password) if parts.password is not None else None,
        "database": database,
        "sslmode": sslmode,
    }


SCHEMA = """
CREATE TABLE IF NOT EXISTS moon_visitors (
    id          TEXT PRIMARY KEY,
    credits     INTEGER NOT NULL DEFAULT 0 CHECK (credits >= 0),
    free_used   BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS moon_orders (
    code        TEXT PRIMARY KEY,
    visitor     TEXT NOT NULL,
    price       INTEGER NOT NULL,
    questions   INTEGER NOT NULL,
    bonus       INTEGER NOT NULL,
    status      TEXT NOT NULL CHECK (status IN ('pending', 'approved', 'rejected')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    decided_at  TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS moon_orders_status_idx ON moon_orders (status, created_at DESC);
CREATE INDEX IF NOT EXISTS moon_orders_visitor_idx ON moon_orders (visitor, created_at DESC);
ALTER TABLE moon_orders ADD COLUMN IF NOT EXISTS slip_attempts INTEGER NOT NULL DEFAULT 0;
ALTER TABLE moon_orders ADD COLUMN IF NOT EXISTS slip_status TEXT;
ALTER TABLE moon_orders ADD COLUMN IF NOT EXISTS slip_note TEXT;
ALTER TABLE moon_orders ADD COLUMN IF NOT EXISTS slip_summary TEXT;
ALTER TABLE moon_orders ADD COLUMN IF NOT EXISTS slip_trans_ref TEXT;
ALTER TABLE moon_orders ADD COLUMN IF NOT EXISTS slip_checked_at TIMESTAMPTZ;
CREATE UNIQUE INDEX IF NOT EXISTS moon_orders_slip_ref_idx ON moon_orders (slip_trans_ref) WHERE slip_trans_ref IS NOT NULL;
CREATE TABLE IF NOT EXISTS moon_users (
    id           TEXT PRIMARY KEY,
    username     TEXT NOT NULL,
    username_key TEXT NOT NULL UNIQUE,
    password     TEXT NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    password_changed_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS moon_sessions (
    token_hash  TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES moon_users (id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at  TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS moon_sessions_user_idx ON moon_sessions (user_id);
ALTER TABLE moon_visitors ADD COLUMN IF NOT EXISTS merged_into TEXT;
"""


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat(timespec="seconds")
    return str(value)


class PostgresCreditService:
    """Same public methods and guarantees as CreditService, backed by Postgres.

    One connection guarded by a lock (the site is a single small process);
    it reconnects once if the server dropped an idle connection.
    """

    kind = "postgres"
    ORDER_COLS = ("code, visitor, price, questions, bonus, status, created_at, decided_at, "
                  "slip_attempts, slip_status, slip_note, slip_summary, slip_trans_ref, slip_checked_at")
    NCOLS = 14

    def __init__(self, url: str):
        self.cfg = parse_database_url(url)
        self.dbapi = _import_pg8000()
        self._lock = threading.RLock()
        self._conn = None
        self._last_used = 0.0
        with self._tx() as cur:
            for stmt in [s for s in SCHEMA.split(";") if s.strip()]:
                cur.execute(stmt)

    # -- connection handling ------------------------------------------------
    def _connect(self):
        import ssl as _ssl

        cfg = self.cfg
        ssl_context = None
        if cfg["sslmode"] != "disable":
            ssl_context = _ssl.create_default_context()
        try:
            conn = self.dbapi.connect(
                host=cfg["host"], port=cfg["port"], user=cfg["user"], password=cfg["password"],
                database=cfg["database"], ssl_context=ssl_context, timeout=15,
                application_name="ask-the-moon",
            )
        except Exception as exc:  # never include the URL; pg8000 messages do not contain it
            hint = ""
            if "28P01" in str(exc):
                pw = cfg.get("password")
                if not pw:
                    hint = " Hint: the URL has no password."
                elif set(pw) <= set("*•●x") or "****" in pw:
                    hint = " Hint: the password in the URL looks masked (asterisks/dots); copy it with the password revealed."
                else:
                    hint = " Hint: the password does not match this role; reset or re-copy it in Neon."
            raise DatabaseConfigError(
                f"Could not connect to Postgres ({type(exc).__name__}: {_safe_msg(exc, cfg)}){hint}"
            ) from None
        conn.autocommit = False
        return conn

    IDLE_PING_SECONDS = 30

    def _ensure_conn(self) -> None:
        """Reconnect if there is no connection or an idle one went stale.

        Statements are never retried, so a dropped connection mid-write can
        not double-charge; it only fails that one request.
        """
        import time

        if self._conn is not None and time.monotonic() - self._last_used > self.IDLE_PING_SECONDS:
            try:
                cur = self._conn.cursor()
                cur.execute("SELECT 1")
                cur.fetchall()
                self._conn.commit()
            except Exception:
                try:
                    self._conn.close()
                except Exception:
                    pass
                self._conn = None
        if self._conn is None:
            self._conn = self._connect()

    @contextmanager
    def _tx(self) -> Iterator[Any]:
        import time

        with self._lock:
            self._ensure_conn()
            conn = self._conn
            try:
                cur = conn.cursor()
                yield cur
                conn.commit()
            except BaseException as exc:
                try:
                    conn.rollback()
                except Exception:
                    self._conn = None
                if isinstance(exc, (self.dbapi.InterfaceError, OSError)):
                    self._conn = None
                raise
            finally:
                self._last_used = time.monotonic()

    def _run(self, fn):
        with self._tx() as cur:
            return fn(cur)

    def _order(self, row) -> dict[str, Any]:
        (code, visitor, price, questions, bonus, status, created, decided,
         attempts, slip_status, slip_note, slip_summary, slip_ref, slip_checked) = row
        try:
            summary = json.loads(slip_summary) if slip_summary else None
        except ValueError:
            summary = None
        return {"code": code, "visitor": visitor, "price": price, "questions": questions, "bonus": bonus,
                "status": status, "createdAt": _iso(created), "decidedAt": _iso(decided),
                "slipAttempts": attempts or 0, "slipStatus": slip_status, "slipNote": slip_note,
                "slipSummary": summary, "slipTransRef": slip_ref, "slipCheckedAt": _iso(slip_checked)}

    # -- visitors -------------------------------------------------------------
    def balance(self, visitor_id: str) -> dict[str, Any]:
        def fn(cur):
            cur.execute("SELECT credits, free_used FROM moon_visitors WHERE id = %s", (visitor_id,))
            row = cur.fetchone()
            return {"credits": int(row[0]), "freeAvailable": not row[1]} if row else {"credits": 0, "freeAvailable": True}
        return self._run(fn)

    def reserve_reading(self, visitor_id: str) -> str:
        def fn(cur):
            cur.execute(
                "UPDATE moon_visitors SET credits = credits - 1 WHERE id = %s AND credits > 0 RETURNING credits",
                (visitor_id,),
            )
            if cur.fetchone():
                return "paid"
            cur.execute(
                "INSERT INTO moon_visitors (id, free_used) VALUES (%s, TRUE) "
                "ON CONFLICT (id) DO UPDATE SET free_used = TRUE WHERE moon_visitors.free_used = FALSE "
                "RETURNING id",
                (visitor_id,),
            )
            if cur.fetchone():
                return "free"
            return None
        kind = self._run(fn)
        if kind is None:
            raise PaymentError("No question credits left.", status=402, code="no_credits")
        return kind

    def release_reading(self, visitor_id: str, kind: str) -> None:
        def fn(cur):
            if kind == "paid":
                cur.execute("UPDATE moon_visitors SET credits = credits + 1 WHERE id = %s", (visitor_id,))
            elif kind == "free":
                cur.execute("UPDATE moon_visitors SET free_used = FALSE WHERE id = %s", (visitor_id,))
        self._run(fn)

    # -- orders ---------------------------------------------------------------
    def create_order(self, visitor_id: str, amount: Any) -> dict[str, Any]:
        pkg = package_for_amount(amount)

        def fn(cur):
            # Serialize order creation per visitor so the reuse check is race-free.
            cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", ("moon-order:" + visitor_id,))
            cur.execute(
                f"SELECT {self.ORDER_COLS} FROM moon_orders WHERE visitor = %s AND status = 'pending'",
                (visitor_id,),
            )
            mine = [self._order(r) for r in cur.fetchall()]
            for o in mine:
                if o["price"] == pkg["price"]:
                    return o
            cur.execute("SELECT count(*) FROM moon_orders WHERE status = 'pending'")
            total = int(cur.fetchone()[0])
            if len(mine) >= MAX_PENDING_PER_VISITOR or total >= MAX_PENDING_TOTAL:
                raise PaymentError("Too many pending orders. Please wait for approval.", 429, "too_many")
            while True:
                code = "M" + "".join(secrets.choice(ORDER_ALPHABET) for _ in range(5))
                cur.execute(
                    "INSERT INTO moon_orders (code, visitor, price, questions, bonus, status) "
                    "VALUES (%s, %s, %s, %s, %s, 'pending') ON CONFLICT (code) DO NOTHING "
                    f"RETURNING {self.ORDER_COLS}",
                    (code, visitor_id, pkg["price"], pkg["questions"], pkg["bonus"]),
                )
                row = cur.fetchone()
                if row:
                    return self._order(row)
        return self._run(fn)

    def visitor_orders(self, visitor_id: str, limit: int = 10) -> list[dict[str, Any]]:
        def fn(cur):
            cur.execute(
                f"SELECT {self.ORDER_COLS} FROM moon_orders WHERE visitor = %s ORDER BY created_at DESC LIMIT %s",
                (visitor_id, limit),
            )
            return [self._order(r) for r in cur.fetchall()]
        return self._run(fn)

    def list_orders(self, status: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        def fn(cur):
            cols = ", ".join("o." + c.strip() for c in self.ORDER_COLS.split(","))
            sql = (f"SELECT {cols}, COALESCE(v.credits, 0), u.username FROM moon_orders o "
                   "LEFT JOIN moon_visitors v ON v.id = o.visitor "
                   "LEFT JOIN moon_users u ON u.id = o.visitor ")
            params: tuple = ()
            if status:
                sql += "WHERE o.status = %s "
                params = (status,)
            sql += "ORDER BY o.created_at DESC LIMIT %s"
            cur.execute(sql, params + (limit,))
            out = []
            for r in cur.fetchall():
                o = self._order(r[: self.NCOLS])
                o["visitorCredits"] = int(r[self.NCOLS])
                o["username"] = r[self.NCOLS + 1]
                out.append(o)
            return out
        return self._run(fn)

    def approve(self, code: str) -> dict[str, Any]:
        def fn(cur):
            cur.execute(f"SELECT {self.ORDER_COLS} FROM moon_orders WHERE code = %s FOR UPDATE", (str(code).upper(),))
            row = cur.fetchone()
            if row is None:
                raise PaymentError("Order not found.", 404, "not_found")
            order = self._order(row)
            if order["status"] == "approved":
                cur.execute("SELECT credits FROM moon_visitors WHERE id = %s", (order["visitor"],))
                r = cur.fetchone()
                return {"order": order, "alreadyApproved": True, "credits": int(r[0]) if r else 0}
            if order["status"] != "pending":
                raise PaymentError("Only pending orders can be approved.", 409, "not_pending")
            cur.execute(
                "INSERT INTO moon_visitors (id, credits) VALUES (%s, %s) "
                "ON CONFLICT (id) DO UPDATE SET credits = moon_visitors.credits + EXCLUDED.credits "
                "RETURNING credits",
                (order["visitor"], int(order["questions"])),
            )
            credits_now = int(cur.fetchone()[0])
            cur.execute(
                f"UPDATE moon_orders SET status = 'approved', decided_at = now() WHERE code = %s RETURNING {self.ORDER_COLS}",
                (order["code"],),
            )
            return {"order": self._order(cur.fetchone()), "alreadyApproved": False, "credits": credits_now}
        return self._run(fn)

    def reject(self, code: str) -> dict[str, Any]:
        def fn(cur):
            cur.execute(f"SELECT {self.ORDER_COLS} FROM moon_orders WHERE code = %s FOR UPDATE", (str(code).upper(),))
            row = cur.fetchone()
            if row is None:
                raise PaymentError("Order not found.", 404, "not_found")
            order = self._order(row)
            if order["status"] == "rejected":
                return {"order": order}
            if order["status"] != "pending":
                raise PaymentError("Only pending orders can be rejected.", 409, "not_pending")
            cur.execute(
                f"UPDATE moon_orders SET status = 'rejected', decided_at = now() WHERE code = %s RETURNING {self.ORDER_COLS}",
                (order["code"],),
            )
            return {"order": self._order(cur.fetchone())}
        return self._run(fn)


    # -- accounts ---------------------------------------------------------------
    def create_user(self, user_id: str, username: str, password_record: str) -> dict[str, Any]:
        def fn(cur):
            cur.execute(
                "INSERT INTO moon_users (id, username, username_key, password) VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (username_key) DO NOTHING RETURNING id",
                (user_id, username, username.lower(), password_record),
            )
            if cur.fetchone() is None:
                raise PaymentError("That username is taken.", 409, "username_taken")
            cur.execute("INSERT INTO moon_visitors (id) VALUES (%s) ON CONFLICT (id) DO NOTHING", (user_id,))
            return {"id": user_id, "username": username}
        return self._run(fn)

    def find_user(self, username: str) -> dict[str, Any] | None:
        def fn(cur):
            cur.execute("SELECT id, username, password FROM moon_users WHERE username_key = %s",
                        (username.strip().lower(),))
            r = cur.fetchone()
            return {"id": r[0], "username": r[1], "password": r[2]} if r else None
        return self._run(fn)

    def set_password(self, user_id: str, password_record: str) -> None:
        self._run(lambda cur: cur.execute(
            "UPDATE moon_users SET password = %s, password_changed_at = now() WHERE id = %s",
            (password_record, user_id)))

    def create_session(self, user_id: str, token_hash: str, expires_at: datetime) -> None:
        def fn(cur):
            cur.execute("DELETE FROM moon_sessions WHERE expires_at < now()")
            cur.execute("INSERT INTO moon_sessions (token_hash, user_id, expires_at) VALUES (%s, %s, %s)",
                        (token_hash, user_id, expires_at))
        self._run(fn)

    def session_user(self, token_hash: str) -> dict[str, Any] | None:
        def fn(cur):
            cur.execute(
                "SELECT u.id, u.username FROM moon_sessions s JOIN moon_users u ON u.id = s.user_id "
                "WHERE s.token_hash = %s AND s.expires_at > now()", (token_hash,))
            r = cur.fetchone()
            return {"id": r[0], "username": r[1]} if r else None
        return self._run(fn)

    def delete_session(self, token_hash: str) -> None:
        self._run(lambda cur: cur.execute("DELETE FROM moon_sessions WHERE token_hash = %s", (token_hash,)))

    def delete_user_sessions(self, user_id: str) -> None:
        self._run(lambda cur: cur.execute("DELETE FROM moon_sessions WHERE user_id = %s", (user_id,)))

    def merge_visitor(self, visitor_id: str, account_id: str) -> dict[str, Any]:
        def fn(cur):
            cur.execute("INSERT INTO moon_visitors (id) VALUES (%s) ON CONFLICT (id) DO NOTHING", (account_id,))
            moved, used = 0, False
            if visitor_id and visitor_id != account_id:
                cur.execute("INSERT INTO moon_visitors (id) VALUES (%s) ON CONFLICT (id) DO NOTHING", (visitor_id,))
                cur.execute("SELECT credits, free_used FROM moon_visitors WHERE id = %s FOR UPDATE", (visitor_id,))
                r = cur.fetchone()
                if r is not None:
                    moved, used = int(r[0]), bool(r[1])
                    cur.execute("UPDATE moon_visitors SET credits = 0, free_used = TRUE, merged_into = %s WHERE id = %s",
                                (account_id, visitor_id))
            cur.execute("UPDATE moon_visitors SET credits = credits + %s, free_used = (free_used OR %s) WHERE id = %s",
                        (moved, used, account_id))
            cur.execute("UPDATE moon_orders SET visitor = %s WHERE visitor = %s AND status = 'pending'",
                        (account_id, visitor_id or ""))
            return {"movedCredits": moved, "movedOrders": cur.rowcount if cur.rowcount and cur.rowcount > 0 else 0}
        return self._run(fn)

    # -- slips ----------------------------------------------------------------
    def begin_slip_check(self, code: str, visitor_id: str, max_attempts: int) -> dict[str, Any]:
        def fn(cur):
            cur.execute(f"SELECT {self.ORDER_COLS} FROM moon_orders WHERE code = %s FOR UPDATE", (str(code).upper(),))
            row = cur.fetchone()
            if row is None:
                raise PaymentError("Order not found.", 404, "not_found")
            order = self._order(row)
            if order["visitor"] != visitor_id:
                raise PaymentError("Order not found.", 404, "not_found")
            if order["status"] == "approved":
                return order
            if order["status"] != "pending":
                raise PaymentError("This order is closed. Please create a new one.", 409, "not_pending")
            if order["slipAttempts"] >= max_attempts:
                raise PaymentError("Too many slip uploads for this order.", 429, "too_many_slips")
            cur.execute(f"UPDATE moon_orders SET slip_attempts = slip_attempts + 1 WHERE code = %s RETURNING {self.ORDER_COLS}",
                        (order["code"],))
            return self._order(cur.fetchone())
        return self._run(fn)

    def set_slip_result(self, code: str, status: str, note: str, summary: dict[str, Any]) -> dict[str, Any]:
        def fn(cur):
            cur.execute(
                "UPDATE moon_orders SET slip_status = %s, slip_note = %s, slip_summary = %s, slip_checked_at = now() "
                f"WHERE code = %s AND status = 'pending' RETURNING {self.ORDER_COLS}",
                (status, note[:200], json.dumps(summary, ensure_ascii=False), str(code).upper()),
            )
            row = cur.fetchone()
            if row is None:
                cur.execute(f"SELECT {self.ORDER_COLS} FROM moon_orders WHERE code = %s", (str(code).upper(),))
                row = cur.fetchone()
            return self._order(row)
        return self._run(fn)

    def trans_ref_used(self, trans_ref: str, except_code: str | None = None) -> bool:
        def fn(cur):
            cur.execute("SELECT 1 FROM moon_orders WHERE slip_trans_ref = %s AND code <> %s",
                        (trans_ref, (except_code or "").upper()))
            return cur.fetchone() is not None
        return self._run(fn)

    def approve_with_slip(self, code: str, trans_ref: str, summary: dict[str, Any]) -> dict[str, Any]:
        def fn(cur):
            # Serialize on the transRef so two orders can't claim one slip at once.
            cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", ("moon-slip:" + trans_ref,))
            cur.execute(f"SELECT {self.ORDER_COLS} FROM moon_orders WHERE code = %s FOR UPDATE", (str(code).upper(),))
            row = cur.fetchone()
            if row is None:
                raise PaymentError("Order not found.", 404, "not_found")
            order = self._order(row)
            cur.execute("SELECT 1 FROM moon_orders WHERE slip_trans_ref = %s AND code <> %s", (trans_ref, order["code"]))
            if cur.fetchone():
                raise PaymentError("This slip was already used.", 409, "duplicate_slip")
            if order["status"] == "approved":
                cur.execute("UPDATE moon_orders SET slip_trans_ref = COALESCE(slip_trans_ref, %s) WHERE code = %s",
                            (trans_ref, order["code"]))
                cur.execute("SELECT credits FROM moon_visitors WHERE id = %s", (order["visitor"],))
                r = cur.fetchone()
                return {"order": order, "alreadyApproved": True, "credits": int(r[0]) if r else 0}
            if order["status"] != "pending":
                raise PaymentError("Only pending orders can be approved.", 409, "not_pending")
            cur.execute(
                "INSERT INTO moon_visitors (id, credits) VALUES (%s, %s) "
                "ON CONFLICT (id) DO UPDATE SET credits = moon_visitors.credits + EXCLUDED.credits RETURNING credits",
                (order["visitor"], int(order["questions"])),
            )
            credits_now = int(cur.fetchone()[0])
            cur.execute(
                "UPDATE moon_orders SET status = 'approved', decided_at = now(), slip_trans_ref = %s, "
                "slip_status = 'verified', slip_note = 'verified by SlipOK', slip_summary = %s, slip_checked_at = now() "
                f"WHERE code = %s RETURNING {self.ORDER_COLS}",
                (trans_ref, json.dumps(summary, ensure_ascii=False), order["code"]),
            )
            return {"order": self._order(cur.fetchone()), "alreadyApproved": False, "credits": credits_now}
        return self._run(fn)


def _safe_msg(exc: Exception, cfg: dict[str, Any]) -> str:
    msg = str(exc)
    for secret in (cfg.get("password"), cfg.get("user"), cfg.get("host")):
        if secret:
            msg = msg.replace(secret, "***")
    return msg[:200]


def make_service(data_dir: str) -> tuple[Any, str, str | None]:
    """Return (service, store name, problem). Uses Postgres when DATABASE_URL is set."""
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        try:
            svc = PostgresCreditService(url)
            return svc, "postgres", None
        except DatabaseConfigError as exc:
            problem = str(exc)
        except Exception as exc:  # e.g. SQL error while creating tables
            problem = f"Postgres setup failed ({type(exc).__name__})"
        return CreditService(JsonStore(data_dir)), "json", problem
    return CreditService(JsonStore(data_dir)), "json", None
