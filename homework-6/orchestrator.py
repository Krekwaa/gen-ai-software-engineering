"""File-based transaction pipeline orchestrator."""

from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

from pipeline.common import account_reference, audit, envelope, write_json
from pipeline.fraud_detector import process_transaction as detect_fraud
from pipeline.settlement import process_transaction as settle
from pipeline.validator import process_transaction as validate

STAGES = (("validator", "fraud_detector", validate), ("fraud_detector", "settlement", detect_fraud), ("settlement", "results", settle))


def prepare_directories(root: Path, clear: bool = True) -> dict[str, Path]:
    shared = root / "shared"
    paths = {name: shared / name for name in ("input", "processing", "output", "results", "audit")}
    if clear and shared.exists():
        shutil.rmtree(shared)
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def sanitize_result(record: dict[str, Any]) -> dict[str, Any]:
    safe = dict(record)
    safe["source_account_ref"] = account_reference(safe.pop("source_account", ""))
    safe["destination_account_ref"] = account_reference(safe.pop("destination_account", ""))
    safe.pop("description", None)
    return safe


def run_pipeline(input_path: Path, root: Path, clear: bool = True) -> dict[str, Any]:
    paths = prepare_directories(root, clear=clear)
    records = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("input file must contain a JSON array")

    outcomes: list[dict[str, Any]] = []
    for index, raw in enumerate(records, start=1):
        transaction_id = str(raw.get("transaction_id", f"UNKNOWN-{index}"))
        input_file = paths["input"] / f"{transaction_id}.json"
        write_json(input_file, envelope(raw, "orchestrator", "validator"))
        current = dict(raw)
        for source, target, stage in STAGES:
            processing_file = paths["processing"] / f"{transaction_id}-{source}.json"
            write_json(processing_file, envelope(current, source, target))
            current = stage(current)
            audit(paths["audit"] / "audit.jsonl", source, transaction_id, current["status"])
            write_json(paths["output"] / f"{transaction_id}-{source}.json", envelope(current, source, target))
            processing_file.unlink()
        safe_result = sanitize_result(current)
        write_json(paths["results"] / f"{transaction_id}.json", envelope(safe_result, "settlement", "complete"))
        outcomes.append(safe_result)

    counts = Counter(item["status"] for item in outcomes)
    summary = {"total": len(outcomes), "status_counts": dict(sorted(counts.items())), "results": outcomes}
    write_json(paths["results"] / "summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the transaction processing pipeline")
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("sample-transactions.json"))
    parser.add_argument("--root", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    summary = run_pipeline(args.input.resolve(), args.root.resolve())
    print("Transaction pipeline completed")
    print(f"Processed: {summary['total']}")
    for status, count in summary["status_counts"].items():
        print(f"  {status}: {count}")
    print("Results: shared/results/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

