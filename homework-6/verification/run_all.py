"""End-to-end acceptance verifier for the Homework 6 capstone.

Run from any directory with: python verification/run_all.py
Returns a non-zero exit code if any required capability or deliverable fails.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path
from typing import Callable

warnings.filterwarnings("ignore")

from fastmcp import Client
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_STATUSES = {"held_for_review": 1, "rejected": 2, "settled": 5}
EXPECTED_SCREENSHOTS = {
    "pipeline-run.png",
    "frontend.png",
    "test-coverage.png",
    "skill-run-pipeline.png",
    "hook-trigger.png",
    "mcp-interaction.png",
}


class VerificationFailure(AssertionError):
    """Raised when an acceptance check fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationFailure(message)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_pipeline() -> str:
    sys.path.insert(0, str(ROOT))
    from orchestrator import run_pipeline

    with tempfile.TemporaryDirectory(prefix="hw6-verify-") as temporary:
        root = Path(temporary)
        summary = run_pipeline(ROOT / "sample-transactions.json", root)
        require(summary["total"] == 8, "pipeline did not process all eight inputs")
        require(summary["status_counts"] == EXPECTED_STATUSES, "unexpected status counts")
        results = root / "shared" / "results"
        transaction_files = sorted(results.glob("TXN*.json"))
        require(len(transaction_files) == 8, "expected eight transaction result files")
        require((results / "summary.json").exists(), "summary.json was not created")
        require(not any((root / "shared" / "processing").iterdir()), "processing directory was not drained")

        text = "".join(path.read_text(encoding="utf-8") for path in transaction_files)
        require("ACC-" not in text, "plaintext account number leaked into final results")
        require("Monthly rent payment" not in text, "description leaked into final results")

        rejected = {item["transaction_id"] for item in summary["results"] if item["status"] == "rejected"}
        require(rejected == {"TXN006", "TXN007"}, "wrong validation rejections")
        held = {item["transaction_id"] for item in summary["results"] if item["status"] == "held_for_review"}
        require(held == {"TXN005"}, "wrong fraud-review decision")
    return "8 inputs -> 5 settled, 1 held, 2 rejected; privacy scan passed"


def check_pytest() -> str:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"], cwd=ROOT, text=True, capture_output=True, encoding="utf-8"
    )
    require(result.returncode == 0, f"pytest/coverage gate failed:\n{result.stdout}\n{result.stderr}")
    coverage_line = next((line.strip() for line in result.stdout.splitlines() if "TOTAL" in line), "coverage >= 80%")
    return f"pytest passed; {coverage_line}"


async def check_mcp_async() -> str:
    server = load_module("verified_pipeline_mcp", ROOT / "mcp" / "server.py")
    async with Client(server.mcp) as client:
        status = await client.call_tool("get_transaction_status", {"transaction_id": "TXN005"})
        require(status.data["found"] is True, "MCP could not find TXN005")
        require(status.data["status"] == "held_for_review", "MCP returned wrong TXN005 status")
        missing = await client.call_tool("get_transaction_status", {"transaction_id": "../../secret"})
        require(missing.data["found"] is False, "MCP accepted an unsafe transaction ID")
        results = await client.call_tool("list_pipeline_results", {})
        require(results.data["total"] == 8, "MCP summary total is wrong")
        resource = await client.read_resource("pipeline://summary")
        require("total=8" in resource[0].text, "MCP summary resource is wrong")
    return "two tools and pipeline://summary passed, including unsafe-ID rejection"


def check_mcp() -> str:
    return asyncio.run(check_mcp_async())


def check_deliverables() -> str:
    required = [
        "specification.md", "agents.md", "orchestrator.py", "research-notes.md", "mcp.json",
        "mcp/server.py", "README.md", "HOWTORUN.md", "PR-DESCRIPTION.md", "docs/presentation.pdf",
    ]
    missing = [item for item in required if not (ROOT / item).exists()]
    require(not missing, f"missing deliverables: {missing}")
    config = json.loads((ROOT / "mcp.json").read_text(encoding="utf-8"))
    require(set(config["mcpServers"]) == {"context7", "pipeline-status"}, "mcp.json must configure both servers")
    screenshots = {path.name for path in (ROOT / "docs" / "screenshots").glob("*.png")}
    require(EXPECTED_SCREENSHOTS <= screenshots, f"missing screenshots: {sorted(EXPECTED_SCREENSHOTS - screenshots)}")
    require(len(PdfReader(ROOT / "docs" / "presentation.pdf").pages) == 6, "presentation must contain six pages")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    require("Vladyslav Shmygelskyy" in readme, "author name missing from README")
    return "required files, dual MCP config, 6 screenshots, 6-page PDF, and author passed"


def main() -> int:
    checks: list[tuple[str, Callable[[], str]]] = [
        ("Pipeline acceptance", check_pipeline),
        ("Unit/integration tests", check_pytest),
        ("Custom MCP", check_mcp),
        ("Deliverables", check_deliverables),
    ]
    failures = 0
    print("Homework 6 complete verification\n")
    for name, check in checks:
        try:
            detail = check()
        except Exception as exc:  # keep running to report every failed area
            failures += 1
            print(f"[FAIL] {name}: {exc}")
        else:
            print(f"[PASS] {name}: {detail}")
    print(f"\nResult: {len(checks) - failures}/{len(checks)} verification groups passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
