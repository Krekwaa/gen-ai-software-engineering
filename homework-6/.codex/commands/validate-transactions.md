---
name: validate-transactions
description: Validate the Homework 6 sample input without running fraud detection or settlement.
---
Validate all records without running the complete pipeline.

1. Run `python -m pipeline.validator --dry-run` from `homework-6`.
2. Report total, valid, and invalid counts.
3. Present a table with transaction ID, validation status, and rejection reasons.
4. Do not reveal account numbers or descriptions.
