"""In-memory banking transaction API for Homework 1."""

from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Banking Transactions API")
transactions: list[dict] = []
SUPPORTED_CURRENCIES = {"USD", "EUR", "GBP", "JPY"}
TYPES = {"deposit", "withdrawal", "transfer"}


class TransactionCreate(BaseModel):
    fromAccount: str
    toAccount: str
    amount: Decimal = Field(gt=0, decimal_places=2)
    currency: str
    type: str

    @field_validator("fromAccount", "toAccount")
    @classmethod
    def account_format(cls, value: str) -> str:
        suffix = value.removeprefix("ACC-")
        if not value.startswith("ACC-") or len(suffix) != 5 or not suffix.isalnum():
            raise ValueError("Account must use ACC-XXXXX format")
        return value

    @field_validator("currency")
    @classmethod
    def currency_code(cls, value: str) -> str:
        value = value.upper()
        if value not in SUPPORTED_CURRENCIES:
            raise ValueError("Invalid currency code")
        return value

    @field_validator("type")
    @classmethod
    def transaction_type(cls, value: str) -> str:
        if value not in TYPES:
            raise ValueError("Invalid transaction type")
        return value


@app.post("/transactions", status_code=201)
def create_transaction(payload: TransactionCreate) -> dict:
    item = payload.model_dump(mode="json")
    item.update(id=str(uuid4()), timestamp=datetime.now(UTC).isoformat(), status="completed")
    transactions.append(item)
    return item


@app.get("/transactions")
def list_transactions(
    accountId: str | None = None,
    type: str | None = None,
    from_date: datetime | None = Query(None, alias="from"),
    to_date: datetime | None = Query(None, alias="to"),
) -> list[dict]:
    result = transactions
    if accountId:
        result = [item for item in result if accountId in (item["fromAccount"], item["toAccount"])]
    if type:
        result = [item for item in result if item["type"] == type]
    if from_date:
        result = [item for item in result if datetime.fromisoformat(item["timestamp"]) >= from_date]
    if to_date:
        result = [item for item in result if datetime.fromisoformat(item["timestamp"]) <= to_date]
    return result


@app.get("/transactions/{transaction_id}")
def get_transaction(transaction_id: str) -> dict:
    for item in transactions:
        if item["id"] == transaction_id:
            return item
    raise HTTPException(status_code=404, detail="Transaction not found")


@app.get("/accounts/{account_id}/balance")
def account_balance(account_id: str) -> dict:
    balance = Decimal("0")
    for item in transactions:
        amount = Decimal(item["amount"])
        if item["toAccount"] == account_id:
            balance += amount
        if item["fromAccount"] == account_id:
            balance -= amount
    return {"accountId": account_id, "balance": str(balance.quantize(Decimal("0.01")))}


@app.get("/accounts/{account_id}/summary")
def account_summary(account_id: str) -> dict:
    related = [item for item in transactions if account_id in (item["fromAccount"], item["toAccount"])]
    deposits = sum((Decimal(item["amount"]) for item in related if item["toAccount"] == account_id), Decimal("0"))
    withdrawals = sum((Decimal(item["amount"]) for item in related if item["fromAccount"] == account_id), Decimal("0"))
    return {"accountId": account_id, "totalDeposits": str(deposits), "totalWithdrawals": str(withdrawals), "transactionCount": len(related), "mostRecentTransaction": max((item["timestamp"] for item in related), default=None)}

