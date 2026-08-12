---
name: run-pipeline
description: Run the Homework 6 transaction pipeline end-to-end and summarize outcomes.
---
Run the transaction processing pipeline end-to-end.

1. Confirm `sample-transactions.json` exists.
2. Run `python orchestrator.py`; the orchestrator safely clears and recreates its own `shared/` directories.
3. Read `shared/results/summary.json`.
4. Report total, settled, held, and rejected counts.
5. List rejected transaction IDs and their validation reasons.
6. Never expose account numbers or descriptions in the response.

