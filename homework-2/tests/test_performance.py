import json
from time import perf_counter

import pytest
from fastapi.testclient import TestClient

from src.backend.app.classifier import ticket_classifier
from src.backend.app.importers import parse_csv_tickets, parse_json_tickets
from src.backend.app.main import app
from src.backend.app.models import Ticket
from src.backend.app.repository import ticket_repository


@pytest.fixture(autouse=True)
def clear_tickets() -> None:
    ticket_repository.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def ticket_payload(index: int) -> dict:
    return {
        "customer_id": f"cust-{index:03d}",
        "customer_email": f"customer{index}@example.com",
        "customer_name": f"Customer {index}",
        "subject": "Cannot access account",
        "description": "I cannot access my account after a password reset.",
    }


def test_create_100_tickets_completes_quickly(client: TestClient) -> None:
    start = perf_counter()

    for index in range(100):
        response = client.post("/tickets", json=ticket_payload(index))
        assert response.status_code == 201

    elapsed = perf_counter() - start
    assert elapsed < 2.5


def test_list_500_tickets_completes_quickly(client: TestClient) -> None:
    for index in range(500):
        response = client.post("/tickets", json=ticket_payload(index))
        assert response.status_code == 201

    start = perf_counter()
    response = client.get("/tickets")
    elapsed = perf_counter() - start

    assert response.status_code == 200
    assert len(response.json()) == 500
    assert elapsed < 0.5


def test_filter_500_tickets_completes_quickly(client: TestClient) -> None:
    for index in range(500):
        priority = "high" if index % 2 == 0 else "low"
        category = "billing_question" if index % 3 == 0 else "account_access"
        payload = ticket_payload(index)
        payload.update({"priority": priority, "category": category})
        response = client.post("/tickets", json=payload)
        assert response.status_code == 201

    start = perf_counter()
    response = client.get("/tickets?category=billing_question&priority=high")
    elapsed = perf_counter() - start

    assert response.status_code == 200
    assert len(response.json()) > 0
    assert elapsed < 0.5


def test_parse_250_csv_records_completes_quickly() -> None:
    rows = [
        "customer_id,customer_email,customer_name,subject,description",
        *[
            f"cust-{index:03d},customer{index}@example.com,Customer {index},"
            "Login issue,I cannot access my account after reset."
            for index in range(250)
        ],
    ]

    start = perf_counter()
    records = parse_csv_tickets("\n".join(rows))
    elapsed = perf_counter() - start

    assert len(records) == 250
    assert elapsed < 0.25


def test_classify_500_tickets_completes_quickly() -> None:
    tickets = [
        Ticket(
            customer_id=f"cust-{index:03d}",
            customer_email=f"customer{index}@example.com",
            customer_name=f"Customer {index}",
            subject="Critical security issue",
            description="This critical security issue is blocking production.",
        )
        for index in range(500)
    ]

    start = perf_counter()
    results = [ticket_classifier.classify(ticket) for ticket in tickets]
    elapsed = perf_counter() - start

    assert len(results) == 500
    assert all(result.priority == "urgent" for result in results)
    assert elapsed < 0.5


def test_parse_250_json_records_completes_quickly() -> None:
    items = [
        {
            "customer_id": f"cust-{index:03d}",
            "customer_email": f"customer{index}@example.com",
            "customer_name": f"Customer {index}",
            "subject": "Invoice request",
            "description": "Please send a copy of my latest invoice.",
        }
        for index in range(250)
    ]

    start = perf_counter()
    records = parse_json_tickets(json.dumps(items))
    elapsed = perf_counter() - start

    assert len(records) == 250
    assert elapsed < 0.25
