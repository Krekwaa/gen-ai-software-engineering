"""FastMCP interface for querying pipeline output."""

from __future__ import annotations

import json
from pathlib import Path

from fastmcp import FastMCP

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "shared" / "results"
mcp = FastMCP("pipeline-status")


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_results() -> dict:
    path = RESULTS_DIR / "summary.json"
    return _read(path) if path.exists() else {"total": 0, "status_counts": {}, "results": []}


@mcp.tool
def get_transaction_status(transaction_id: str) -> dict:
    """Return the current privacy-safe result for a transaction ID."""
    normalized = transaction_id.strip().upper()
    if not normalized or any(char not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for char in normalized):
        return {"found": False, "error": "invalid transaction_id"}
    path = RESULTS_DIR / f"{normalized}.json"
    if not path.exists():
        return {"found": False, "transaction_id": normalized}
    return {"found": True, **_read(path)["data"]}


@mcp.tool
def list_pipeline_results() -> dict:
    """Return aggregate status counts and transaction summaries."""
    return _load_results()


@mcp.resource("pipeline://summary")
def pipeline_summary() -> str:
    """Return the latest run summary as readable text."""
    summary = _load_results()
    counts = ", ".join(f"{key}={value}" for key, value in summary["status_counts"].items()) or "no results"
    return f"Latest pipeline run: total={summary['total']}; {counts}."


if __name__ == "__main__":
    mcp.run()
