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
        "customer_name": "Customer One",
        "subject": "Cannot access account",
        "description": "I cannot access my account after password reset.",
    }
    payload.update(overrides)
    return payload


def create_ticket(client: TestClient, **overrides: object) -> dict:
    response = client.post("/tickets", json=valid_ticket_payload(**overrides))
    assert response.status_code == 201
    return response.json()


def test_auto_classify_endpoint_returns_result_and_updates_ticket(client: TestClient) -> None:
    ticket = create_ticket(client)

    classify_response = client.post(f"/tickets/{ticket['id']}/auto-classify")
    updated_ticket = client.get(f"/tickets/{ticket['id']}").json()

    assert classify_response.status_code == 200
    result = classify_response.json()
    assert result["category"] == "account_access"
    assert result["priority"] == "urgent"
    assert result["confidence"] > 0
    assert "cannot access" in result["keywords_found"]
    assert updated_ticket["category"] == "account_access"
    assert updated_ticket["priority"] == "urgent"
    assert updated_ticket["classification_confidence"] == result["confidence"]


def test_auto_classify_returns_404_for_missing_ticket(client: TestClient) -> None:
    response = client.post("/tickets/00000000-0000-0000-0000-000000000000/auto-classify")

    assert response.status_code == 404


def test_create_ticket_can_auto_classify(client: TestClient) -> None:
    response = client.post(
        "/tickets",
        json=valid_ticket_payload(
            auto_classify=True,
            subject="Production down",
            description="Production down after a critical security change.",
        ),
    )

    assert response.status_code == 201
    ticket = response.json()
    assert ticket["priority"] == "urgent"
    assert ticket["classification_confidence"] is not None


def test_manual_category_or_priority_update_marks_override(client: TestClient) -> None:
    ticket = create_ticket(client, auto_classify=True)

    response = client.put(
        f"/tickets/{ticket['id']}",
        json={"category": "billing_question", "priority": "low"},
    )

    assert response.status_code == 200
    assert response.json()["classification_overridden"] is True


def test_update_without_classification_change_does_not_mark_override(client: TestClient) -> None:
    ticket = create_ticket(client, auto_classify=True)

    response = client.put(
        f"/tickets/{ticket['id']}",
        json={
            "category": ticket["category"],
            "priority": ticket["priority"],
            "assigned_to": "Agent One",
        },
    )

    assert response.status_code == 200
    assert response.json()["classification_overridden"] is False


def test_classification_logs_are_stored(client: TestClient) -> None:
    ticket = create_ticket(client)

    client.post(f"/tickets/{ticket['id']}/auto-classify")
    response = client.get(f"/tickets/{ticket['id']}/classification-logs")

    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 1
    assert logs[0]["ticket_id"] == ticket["id"]
    assert logs[0]["category"] == "account_access"


def test_classification_logs_return_404_for_missing_ticket(client: TestClient) -> None:
    response = client.get("/tickets/00000000-0000-0000-0000-000000000000/classification-logs")

    assert response.status_code == 404


def test_import_respects_auto_classify_flag(client: TestClient) -> None:
    response = client.post(
        "/tickets/import",
        files={
            "file": (
                "tickets.json",
                """
                [
                  {
                    "customer_id": "cust-001",
                    "customer_email": "customer@example.com",
                    "customer_name": "Customer One",
                    "subject": "Security issue",
                    "description": "This is a critical security problem.",
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
    assert response.json()["successful"] == 1
    assert tickets[0]["priority"] == "urgent"
    assert tickets[0]["classification_confidence"] is not None
