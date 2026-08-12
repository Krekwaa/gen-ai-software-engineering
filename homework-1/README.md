# Homework 1: Banking Transactions API

**Student:** Vladyslav Shmygelskyy  
**AI tool:** Codex  
**Submitted:** August 2026

This project implements a small FastAPI banking transaction service backed by in-memory storage. It supports creation, lookup, combined history filters, account balances, and the optional account-summary endpoint.

Validation enforces positive Decimal amounts with at most two fractional digits, `ACC-XXXXX` account identifiers, supported ISO 4217 currencies, and known transaction types. The included pytest program verifies the complete transaction workflow plus negative validation and missing-resource behavior.

## Endpoints

- `POST /transactions`
- `GET /transactions`
- `GET /transactions/{id}`
- `GET /accounts/{accountId}/balance`
- `GET /accounts/{accountId}/summary`

See [HOWTORUN.md](HOWTORUN.md) and `demo/sample-requests.http`.

