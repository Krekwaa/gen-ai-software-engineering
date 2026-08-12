"""Shared contracts and safe audit helpers for pipeline stages."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from uuid import uuid4

SUPPORTED_CURRENCIES = {"USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD"}
REQUIRED_FIELDS = {
    "transaction_id",
    "timestamp",
    "source_account",
    "destination_account",
    "amount",
    "currency",
    "transaction_type",
}


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def parse_amount(value: Any) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError("amount must be a decimal number") from exc
    if not amount.is_finite():
        raise ValueError("amount must be finite")
    return amount


def parse_timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp must be an ISO 8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp must be valid ISO 8601") from exc
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(UTC)


def account_reference(value: str) -> str:
    """Return a non-reversible short reference suitable for logs and results."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def envelope(data: dict[str, Any], source: str, target: str) -> dict[str, Any]:
    return {
        "message_id": str(uuid4()),
        "timestamp": utc_now(),
        "source_stage": source,
        "target_stage": target,
        "message_type": "transaction",
        "data": data,
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temporary.replace(path)


def audit(log_path: Path, stage: str, transaction_id: str, outcome: str) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": utc_now(),
        "stage": stage,
        "transaction_id": transaction_id,
        "outcome": outcome,
    }
    with log_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record) + "\n")

