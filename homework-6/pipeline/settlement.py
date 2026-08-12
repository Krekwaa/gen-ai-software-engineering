"""Settlement decision stage."""

from __future__ import annotations

from decimal import ROUND_HALF_UP
from typing import Any

from pipeline.common import parse_amount, utc_now


def process_transaction(record: dict[str, Any]) -> dict[str, Any]:
    result = dict(record)
    if result.get("status") == "rejected":
        result["settlement"] = {"outcome": "not_attempted", "reason": "validation_failed"}
        return result
    if result.get("fraud", {}).get("risk_level") == "high":
        result["status"] = "held_for_review"
        result["settlement"] = {"outcome": "held", "reason": "high_fraud_risk"}
        return result

    amount = parse_amount(result["amount"]).quantize(parse_amount("0.01"), rounding=ROUND_HALF_UP)
    result["amount"] = format(amount, "f")
    result["status"] = "settled"
    result["settlement"] = {"outcome": "completed", "settled_at": utc_now()}
    return result

