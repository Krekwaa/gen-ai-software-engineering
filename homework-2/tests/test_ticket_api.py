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


def valid_ticket_payload(**overrides: object) -> dict:
    payload = {
        "customer_id": "cust-001",
        "customer_email": "customer@example.com",
        "customer_name": "Ada Lovelace",
        "subject": "Cannot access account",
        "description": "I cannot access my account after password reset.",
        "category": "account_access",
        "priority": "high",
        "status": "new",
        "tags": ["login", "urgent"],
        "metadata": {
            "source": "web_form",
            "browser": "Chrome",
            "device_type": "desktop",
        },
    }
    payload.update(overrides)
    return payload


def create_ticket(client: TestClient, **overrides: object) -> dict:
    response = client.post("/tickets", json=valid_ticket_payload(**overrides))
    assert response.status_code == 201
    return response.json()


def test_create_ticket_returns_created_ticket(client: TestClient) -> None:
    ticket = create_ticket(client)

    assert ticket["id"]
    assert ticket["customer_email"] == "customer@example.com"
    assert ticket["category"] == "account_access"
    assert ticket["priority"] == "high"
    assert ticket["created_at"]
    assert ticket["updated_at"]


def test_create_ticket_rejects_invalid_payload(client: TestClient) -> None:
    response = client.post(
        "/tickets",
        json=valid_ticket_payload(customer_email="invalid-email"),
    )

    assert response.status_code == 422


def test_list_tickets_returns_all_tickets(client: TestClient) -> None:
    create_ticket(client, customer_id="cust-001", customer_email="one@example.com")
    create_ticket(client, customer_id="cust-002", customer_email="two@example.com")

    response = client.get("/tickets")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_tickets_filters_by_category_priority_and_status(client: TestClient) -> None:
    create_ticket(
        client,
        customer_id="cust-001",
        customer_email="one@example.com",
        category="billing_question",
        priority="low",
        status="closed",
    )
    create_ticket(
        client,
        customer_id="cust-002",
        customer_email="two@example.com",
        category="account_access",
        priority="high",
        status="new",
    )

    response = client.get("/tickets?category=account_access&priority=high&status=new")

    assert response.status_code == 200
    tickets = response.json()
    assert len(tickets) == 1
    assert tickets[0]["customer_id"] == "cust-002"


def test_get_ticket_returns_specific_ticket(client: TestClient) -> None:
    created = create_ticket(client)

    response = client.get(f"/tickets/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_ticket_returns_404_for_missing_ticket(client: TestClient) -> None:
    response = client.get("/tickets/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found."


def test_get_ticket_rejects_invalid_uuid(client: TestClient) -> None:
    response = client.get("/tickets/not-a-uuid")

    assert response.status_code == 422


def test_update_ticket_changes_existing_ticket(client: TestClient) -> None:
    created = create_ticket(client)

    response = client.put(
        f"/tickets/{created['id']}",
        json={"status": "in_progress", "assigned_to": "Agent One"},
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["status"] == "in_progress"
    assert updated["assigned_to"] == "Agent One"
    assert updated["updated_at"] >= created["updated_at"]


def test_update_ticket_returns_404_for_missing_ticket(client: TestClient) -> None:
    response = client.put(
        "/tickets/00000000-0000-0000-0000-000000000000",
        json={"status": "closed"},
    )

    assert response.status_code == 404


def test_delete_ticket_removes_ticket(client: TestClient) -> None:
    created = create_ticket(client)

    delete_response = client.delete(f"/tickets/{created['id']}")
    get_response = client.get(f"/tickets/{created['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_delete_ticket_returns_404_for_missing_ticket(client: TestClient) -> None:
    response = client.delete("/tickets/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
