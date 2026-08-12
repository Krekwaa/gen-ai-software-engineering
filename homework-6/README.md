# AI-Powered Transaction Processing Pipeline

**Created by Vladyslav Shmygelskyy**

This capstone implements an auditable file-based transaction workflow. Eight synthetic payments pass through validation, deterministic fraud scoring, and settlement. Every input receives a final outcome—even when validation rejects it—and privacy-safe results can be inspected through a web dashboard or MCP tools.

The project also demonstrates an AI-assisted engineering workflow: a specification skill establishes behavior, context7 provides framework research, implementation and test agents follow project rules, a pre-push hook enforces coverage, and a documentation agent maintains the submission evidence.

## Pipeline responsibilities

- **Validation:** checks required fields, positive Decimal amounts, supported ISO 4217 codes, timestamps, and identifiers.
- **Fraud detection:** scores high value, unusual UTC time, and cross-border USD indicators; high risk is held.
- **Settlement:** rejects invalid records, holds high-risk transactions, and settles eligible amounts using `ROUND_HALF_UP`.
- **Orchestrator:** moves standard JSON envelopes through shared directories, writes safe audit events, and produces final results.
- **Dashboard and MCP:** expose aggregate and per-transaction outcomes without plaintext account data.

## Architecture

```text
sample-transactions.json
          |
          v
  shared/input/ -> [Validator] -> [Fraud Detector] -> [Settlement]
                       |                 |                 |
                       +------ standard JSON envelopes ---+
                                         |
                                         v
                              shared/results/ + audit
                                  /                 \
                                 v                   v
                         FastAPI dashboard      FastMCP server
```

## Technology stack

| Area | Technology |
|---|---|
| Language | Python 3.11+ |
| Web UI | FastAPI, Uvicorn, HTML/CSS/JavaScript |
| MCP | FastMCP and context7 |
| Tests | pytest, pytest-cov |
| Data | JSON/JSONL, `decimal.Decimal`, UUID4 |
| Automation | Codex skills and Git pre-push hook |

## Verified result

The supplied dataset produces 8 final results: 5 settled, 1 held for review, and 2 rejected. The test suite contains 27 tests and currently reports 97.84% coverage.

See [HOWTORUN.md](HOWTORUN.md) for setup and demonstration steps. Evidence is under `docs/screenshots/`, and the presentation is `docs/presentation.pdf`.

For one-command acceptance testing, run `python verification/run_all.py`.

## Security notes

This is a teaching demonstration, not a production banking system. Plaintext account values and descriptions are removed from final results; account references are SHA-256-derived aliases. Audit events contain only timestamp, stage, transaction ID, and outcome. Production use would require formal threat modeling, key-managed pseudonymization, authentication, authorization, durable storage, reconciliation, and qualified compliance review.
