"""Transparent, deterministic fraud risk scoring stage."""

from __future__ import annotations

from typing import Any

from pipeline.common import parse_amount, parse_timestamp


def process_transaction(record: dict[str, Any]) -> dict[str, Any]:
    if record.get("status") == "rejected":
        return record

    score = 0
    indicators: list[str] = []
    amount = parse_amount(record["amount"])
    if amount >= 50_000:
        score += 70
        indicators.append("very_high_value")
    elif amount > 10_000:
        score += 45
        indicators.append("high_value")

    hour = parse_timestamp(record["timestamp"]).hour
    if hour < 6 or hour >= 23:
        score += 30
        indicators.append("unusual_time")

    country = record.get("metadata", {}).get("country")
    if country and country != "US" and record.get("currency") == "USD":
        score += 25
        indicators.append("cross_border")

    score = min(score, 100)
    level = "high" if score >= 60 else "medium" if score >= 30 else "low"
    result = dict(record)
    result["status"] = "fraud_review" if level == "high" else "risk_scored"
    result["fraud"] = {"risk_score": score, "risk_level": level, "indicators": indicators}
    return result

