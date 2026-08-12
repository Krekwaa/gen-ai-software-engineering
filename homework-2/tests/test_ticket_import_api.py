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


def upload(client: TestClient, filename: str, content: str) -> object:
    return client.post(
        "/tickets/import",
        files={"file": (filename, content, "text/plain")},
    )


def test_import_csv_creates_valid_tickets(client: TestClient) -> None:
    response = upload(
        client,
        "tickets.csv",
        (
            "customer_id,customer_email,customer_name,subject,description,category,priority,status\n"
            "cust-001,one@example.com,One User,Login issue,"
            "I cannot access my account after password reset.,account_access,high,new\n"
            "cust-002,two@example.com,Two User,Invoice request,"
            "Please send me a copy of my latest invoice.,billing_question,medium,new\n"
        ),
    )

    assert response.status_code == 200
    assert response.json()["total_records"] == 2
    assert response.json()["successful"] == 2
    assert len(client.get("/tickets").json()) == 2


def test_import_json_creates_valid_tickets(client: TestClient) -> None:
    response = upload(
        client,
        "tickets.json",
        """
        [
          {
            "customer_id": "cust-001",
            "customer_email": "one@example.com",
            "customer_name": "One User",
            "subject": "Crash report",
            "description": "The desktop app crashes when I export a report.",
            "category": "bug_report",
            "priority": "high"
          }
        ]
        """,
    )

    assert response.status_code == 200
    assert response.json()["successful"] == 1


def test_import_xml_creates_valid_tickets(client: TestClient) -> None:
    response = upload(
        client,
        "tickets.xml",
        """
        <tickets>
          <ticket>
            <customer_id>cust-001</customer_id>
            <customer_email>one@example.com</customer_email>
            <customer_name>One User</customer_name>
            <subject>Feature request</subject>
            <description>I would like a suggestion dashboard for reports.</description>
            <category>feature_request</category>
            <priority>low</priority>
          </ticket>
        </tickets>
        """,
    )

    assert response.status_code == 200
    assert response.json()["successful"] == 1


def test_import_reports_validation_failures_without_aborting(client: TestClient) -> None:
    response = upload(
        client,
        "tickets.csv",
        (
            "customer_id,customer_email,customer_name,subject,description\n"
            "cust-001,one@example.com,One User,Valid subject,"
            "This is a valid description for the ticket.\n"
            "cust-002,not-email,Two User,Bad email,"
            "This row has invalid email data.\n"
        ),
    )

    body = response.json()
    assert response.status_code == 200
    assert body["total_records"] == 2
    assert body["successful"] == 1
    assert body["failed"] == 1
    assert body["errors"][0]["record"] == 2


def test_import_rejects_unsupported_file_type(client: TestClient) -> None:
    response = upload(client, "tickets.txt", "not supported")

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported import format. Use CSV, JSON, or XML."


def test_import_rejects_malformed_json(client: TestClient) -> None:
    response = upload(client, "tickets.json", "{bad json")

    assert response.status_code == 400
    assert "Malformed JSON" in response.json()["detail"]
