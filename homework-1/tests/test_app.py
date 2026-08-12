from fastapi.testclient import TestClient

from src.app import app, transactions

client = TestClient(app)
VALID = {"fromAccount":"ACC-12345","toAccount":"ACC-67890","amount":"100.50","currency":"USD","type":"transfer"}


def setup_function():
    transactions.clear()


def test_complete_transaction_workflow():
    created = client.post("/transactions", json=VALID)
    assert created.status_code == 201
    transaction_id = created.json()["id"]
    assert client.get(f"/transactions/{transaction_id}").status_code == 200
    assert len(client.get("/transactions?accountId=ACC-12345&type=transfer").json()) == 1
    assert client.get("/accounts/ACC-12345/balance").json()["balance"] == "-100.50"
    assert client.get("/accounts/ACC-67890/summary").json()["transactionCount"] == 1


def test_validation_and_not_found():
    bad = dict(VALID, amount="-1", currency="XYZ", fromAccount="wrong")
    assert client.post("/transactions", json=bad).status_code == 422
    assert client.get("/transactions/missing").status_code == 404

