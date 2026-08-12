"""Validation stage for raw transaction records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pipeline.common import REQUIRED_FIELDS, SUPPORTED_CURRENCIES, parse_amount, parse_timestamp


def process_transaction(record: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    missing = sorted(REQUIRED_FIELDS - record.keys())
    if missing:
        reasons.append(f"missing required fields: {', '.join(missing)}")

    if "amount" in record:
        try:
            if parse_amount(record["amount"]) <= 0:
                reasons.append("amount must be greater than zero")
        except ValueError as exc:
            reasons.append(str(exc))

    currency = record.get("currency")
    if currency not in SUPPORTED_CURRENCIES:
        reasons.append("currency must be a supported ISO 4217 code")

    if "timestamp" in record:
        try:
            parse_timestamp(record["timestamp"])
        except ValueError as exc:
            reasons.append(str(exc))

    for field in ("transaction_id", "source_account", "destination_account", "transaction_type"):
        if field in record and (not isinstance(record[field], str) or not record[field].strip()):
            reasons.append(f"{field} must be a non-empty string")

    result = dict(record)
    result["status"] = "validated" if not reasons else "rejected"
    result["validation"] = {"valid": not reasons, "reasons": reasons}
    return result


def dry_run(source: Path) -> list[dict[str, Any]]:
    records = json.loads(source.read_text(encoding="utf-8"))
    return [process_transaction(record) for record in records]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate transaction input")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--input", type=Path, default=Path("sample-transactions.json"))
    args = parser.parse_args()
    results = dry_run(args.input)
    valid = sum(item["validation"]["valid"] for item in results)
    print(f"Total: {len(results)} | Valid: {valid} | Invalid: {len(results) - valid}")
    for item in results:
        reasons = "; ".join(item["validation"]["reasons"]) or "-"
        print(f"{item.get('transaction_id', '<missing>'):<12} {item['status']:<10} {reasons}")
    return 0 if args.dry_run or valid == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

