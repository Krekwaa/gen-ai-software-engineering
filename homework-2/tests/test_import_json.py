import pytest

from src.backend.app.importers import ImportParseError, parse_json_tickets


def test_parse_json_tickets_accepts_array() -> None:
    records = parse_json_tickets(
        """
        [
          {
            "customer_id": "cust-001",
            "customer_email": "one@example.com",
            "customer_name": "One User",
            "subject": "Billing question",
            "description": "I need a copy of my latest invoice.",
            "tags": "invoice,billing"
          }
        ]
        """
    )

    assert len(records) == 1
    assert records[0]["tags"] == ["invoice", "billing"]


def test_parse_json_tickets_accepts_tickets_wrapper() -> None:
    records = parse_json_tickets(
        """
        {
          "tickets": [
            {
              "customer_id": "cust-002",
              "customer_email": "two@example.com",
              "customer_name": "Two User",
              "subject": "App crash",
              "description": "The mobile app crashes after login.",
              "metadata": {"source": "chat", "device_type": "mobile"}
            }
          ]
        }
        """
    )

    assert records[0]["metadata"]["source"] == "chat"


def test_parse_json_tickets_rejects_malformed_json() -> None:
    with pytest.raises(ImportParseError, match="Malformed JSON"):
        parse_json_tickets("{bad json")


def test_parse_json_tickets_rejects_non_array_payload() -> None:
    with pytest.raises(ImportParseError, match="tickets array"):
        parse_json_tickets('{"customer_id": "cust-001"}')
