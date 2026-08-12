# AI-Powered Transaction Processing Pipeline Specification

> Implement the Low-Level Tasks in order and verify them against the objectives below.

## High-Level Objective

Build a privacy-conscious file-based pipeline that validates, risk-scores, and settles transaction records while exposing final outcomes through a web dashboard and MCP interface.

## Mid-Level Objectives

- MO-1: Process every record in `sample-transactions.json` through ordered validation, fraud-detection, and settlement decisions, producing exactly one final transaction result per input.
- MO-2: Reject malformed transactions, including non-positive amounts and unsupported currency codes, with stable, explicit reasons.
- MO-3: Assign a deterministic 0-100 risk score using high-value, unusual-time, and cross-border indicators; hold high-risk transactions for human review.
- MO-4: Maintain JSON stage envelopes and UTC audit records containing timestamp, stage, transaction ID, and outcome without plaintext accounts or descriptions.
- MO-5: Provide a usable web dashboard, queryable MCP tools/resource, and an isolated automated test suite with at least 90% target coverage and an enforced 80% push gate.

## Implementation Notes

- Use Python `Decimal`; never use binary floating point for transaction amounts.
- Accept only the allowlisted ISO 4217 codes USD, EUR, GBP, JPY, CHF, CAD, and AUD for this demonstration.
- Use ISO 8601 timestamps with timezone information and normalize generated timestamps to UTC with a `Z` suffix.
- Wrap stage messages with UUID4 message IDs, source and target stage names, message type, timestamp, and data.
- Audit logs may contain only timestamp, stage, transaction ID, and outcome. Hash account references before final storage; never log accounts or descriptions.
- Validation failures are final rejections. High fraud risk produces `held_for_review`; otherwise settlement produces `settled`.
- Write JSON atomically through a temporary file and isolate tests with temporary directories.

## Context

### Beginning state

- `sample-transactions.json` contains eight synthetic raw transaction records.
- No starter implementation or shared runtime directories exist.

### Ending state

- `shared/input/`, `shared/processing/`, `shared/output/`, `shared/results/`, and `shared/audit/` implement the file protocol.
- Eight privacy-safe transaction results and one `summary.json` exist in `shared/results/`.
- The pipeline, dashboard, MCP server, Codex skills, tests, coverage hook, documentation, evidence, and presentation are runnable from the repository.
- Automated coverage is at least 80%, with at least 90% targeted.

## Low-Level Tasks

### LLT-1: Validation Stage

Task: Validate raw transaction structure and domain values.

Prompt: "Create a Python validator that copies its input, checks all required transaction fields, parses amount with Decimal, requires amount greater than zero, validates an allowlisted ISO 4217 currency, requires a timezone-aware ISO 8601 timestamp and non-empty identifiers, then returns validated or rejected status with every rejection reason. Add a dry-run module CLI."

File to CREATE: `pipeline/validator.py`

Function to CREATE: `process_transaction(record: dict) -> dict`

Details: Preserve the original raw object during processing, accumulate rather than short-circuit validation errors, and never print account fields in CLI summaries.

### LLT-2: Fraud Detection Stage

Task: Calculate a transparent transaction risk score.

Prompt: "Create a deterministic Python fraud stage that bypasses rejected records, scores high and very-high amounts, unusual UTC hours, and cross-border USD activity, caps risk at 100, assigns low/medium/high levels, records named indicators, and sends high-risk transactions to review."

File to CREATE: `pipeline/fraud_detector.py`

Function to CREATE: `process_transaction(record: dict) -> dict`

Details: Amount above 10,000 adds 45; amount at least 50,000 adds 70 instead; hours before 06:00 or at/after 23:00 add 30; non-US USD adds 25; risk of 60 or above is high.

### LLT-3: Settlement Stage

Task: Finalize eligible transactions or hold/reject them safely.

Prompt: "Create a settlement stage that does not attempt rejected records, holds high-risk records, and settles all other validated records after quantizing their Decimal amount to two places using ROUND_HALF_UP. Include a UTC settlement timestamp."

File to CREATE: `pipeline/settlement.py`

Function to CREATE: `process_transaction(record: dict) -> dict`

Details: Final states are `rejected`, `held_for_review`, and `settled`; every state must carry a settlement outcome or reason.

### LLT-4: Orchestration and File Protocol

Task: Run all stages and materialize inspectable artifacts.

Prompt: "Create an orchestrator that safely recreates only its project shared directory, loads a JSON array, writes standard envelopes across input/processing/output/results, removes processing claims, writes a safe audit JSONL file, strips plaintext accounts and descriptions from final results, and creates a deterministic summary."

File to CREATE: `orchestrator.py`

Function to CREATE: `run_pipeline(input_path: Path, root: Path, clear: bool = True) -> dict`

Details: Use atomic JSON writes and produce one `{transaction_id}.json` per input plus `summary.json`.

### LLT-5: Dashboard and MCP Query Surface

Task: Make the pipeline observable without exposing sensitive values.

Prompt: "Create a FastAPI dashboard with a run action and results table, plus a FastMCP server exposing get_transaction_status, list_pipeline_results, and pipeline://summary using only privacy-safe result files."

File to CREATE: `frontend/app.py` and `mcp/server.py`

Function to CREATE: `dashboard()`, `api_run()`, `get_transaction_status()`, `list_pipeline_results()`, and `pipeline_summary()`

Details: Dashboard must show totals and decisions; MCP transaction IDs must be sanitized before constructing paths.
