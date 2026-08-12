"""FastAPI dashboard for transaction pipeline results."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from orchestrator import run_pipeline

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "shared" / "results"
app = FastAPI(title="Transaction Pipeline Dashboard")


def load_summary() -> dict:
    summary = RESULTS_DIR / "summary.json"
    if not summary.exists():
        return {"total": 0, "status_counts": {}, "results": []}
    return json.loads(summary.read_text(encoding="utf-8"))


@app.get("/api/results")
def api_results() -> dict:
    return load_summary()


@app.post("/api/run")
def api_run() -> dict:
    source = PROJECT_ROOT / "sample-transactions.json"
    if not source.exists():
        raise HTTPException(status_code=404, detail="sample-transactions.json not found")
    return run_pipeline(source, PROJECT_ROOT)


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return (Path(__file__).with_name("index.html")).read_text(encoding="utf-8")

