# Homework 1 - Banking Transactions API

## Summary

Implemented the required in-memory banking REST API with transaction creation and lookup, combined history filters, account balances, and the optional account summary. Input validation covers Decimal amounts, account format, currencies, and transaction types.

## AI-assisted workflow

Codex was used to decompose the endpoint requirements, generate a small FastAPI implementation, and create executable acceptance tests. I verified the output locally rather than relying only on generated code.

## Verification

```powershell
cd homework-1
python -m pip install -r requirements.txt
python -m pytest -q
python -m uvicorn src.app:app --reload
```

## Evidence

![AI interaction](docs/screenshots/ai-prompt-1.png)

## Challenges

Money uses `Decimal` rather than binary floating point, and filters remain composable. Storage is intentionally in-memory because the assignment excludes a database.

