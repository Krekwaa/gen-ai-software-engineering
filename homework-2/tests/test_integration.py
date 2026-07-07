from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from src.backend.app.main import app
from src.backend.app.repository import ticket_repository


@pytest.fixture(autouse=True)
def clear_tickets() -> None:
    ticket_repository.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def ticket_payload(index: int, **overrides: object) -> dict:
    payload = {
        "customer_id": f"cust-{index:03d}",
        "customer_email": f"customer{index}@example.com",
        "customer_name": f"Customer {index}",
        "subject": "Cannot access account",
        "description": "I cannot access my account after resetting my password.",
        "category": "other",
        "priority": "medium",
        "status": "new",
    }
    payload.update(overrides)
    return payload


def test_complete_ticket_lifecycle_workflow(client: TestClient) -> None:
    created = client.post("/tickets", json=ticket_payload(1)).json()

    classified = client.post(f"/tickets/{created['id']}/auto-classify")
    updated = client.put(
        f"/tickets/{created['id']}",
        json={"status": "resolved", "assigned_to": "Agent One"},
    )
    fetched = client.get(f"/tickets/{created['id']}")
    deleted = client.delete(f"/tickets/{created['id']}")
    missing = client.get(f"/tickets/{created['id']}")

    assert classified.status_code == 200
    assert classified.json()["priority"] == "urgent"
    assert updated.status_code == 200
    assert updated.json()["resolved_at"] is not None
    assert fetched.status_code == 200
    assert deleted.status_code == 204
    assert missing.status_code == 404


def test_bulk_import_with_auto_classification_verification(client: TestClient) -> None:
    response = client.post(
        "/tickets/import",
        files={
            "file": (
                "tickets.json",
                """
                [
                  {
                    "customer_id": "cust-001",
                    "customer_email": "one@example.com",
                    "customer_name": "One User",
                    "subject": "Production down",
                    "description": "Production down after a critical security update.",
                    "auto_classify": true
                  },
                  {
                    "customer_id": "cust-002",
                    "customer_email": "two@example.com",
                    "customer_name": "Two User",
                    "subject": "Invoice request",
                    "description": "Please send my latest invoice for billing review.",
                    "auto_classify": true
                  }
                ]
                """,
                "application/json",
            )
        },
    )

    tickets = client.get("/tickets").json()

    assert response.status_code == 200
    assert response.json()["successful"] == 2
    assert {ticket["priority"] for ticket in tickets} == {"urgent", "medium"}
    assert all(ticket["classification_confidence"] is not None for ticket in tickets)


def test_concurrent_create_operations_handle_20_requests() -> None:
    def create(index: int) -> int:
        with TestClient(app) as local_client:
            response = local_client.post("/tickets", json=ticket_payload(index))
            return response.status_code

    with ThreadPoolExecutor(max_workers=8) as executor:
        statuses = list(executor.map(create, range(1, 21)))

    with TestClient(app) as local_client:
        tickets = local_client.get("/tickets").json()

    assert statuses == [201] * 20
    assert len(tickets) == 20


def test_combined_filtering_by_category_and_priority(client: TestClient) -> None:
    client.post(
        "/tickets",
        json=ticket_payload(1, category="billing_question", priority="low"),
    )
    client.post(
        "/tickets",
        json=ticket_payload(2, category="billing_question", priority="high"),
    )
    client.post(
        "/tickets",
        json=ticket_payload(3, category="account_access", priority="high"),
    )

    response = client.get("/tickets?category=billing_question&priority=high")

    assert response.status_code == 200
    tickets = response.json()
    assert len(tickets) == 1
    assert tickets[0]["customer_id"] == "cust-002"


def test_validation_error_does_not_corrupt_existing_ticket_data(client: TestClient) -> None:
    created = client.post("/tickets", json=ticket_payload(1)).json()

    invalid_update = client.put(
        f"/tickets/{created['id']}",
        json={"description": "short"},
    )
    fetched = client.get(f"/tickets/{created['id']}")

    assert invalid_update.status_code == 422
    assert fetched.status_code == 200
    assert fetched.json()["description"] == created["description"]
