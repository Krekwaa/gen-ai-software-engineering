import pytest

from src.backend.app.importers import ImportParseError, parse_csv_tickets


def test_parse_csv_tickets_returns_records() -> None:
    csv_text = (
        "customer_id,customer_email,customer_name,subject,description,category,"
        "priority,status,tags,metadata_source,browser,device_type\n"
        "cust-001,one@example.com,One User,Login broken,"
        "I cannot access my account after reset.,account_access,high,new,"
        "login;password,web_form,Chrome,desktop\n"
    )

    records = parse_csv_tickets(csv_text)

    assert len(records) == 1
    assert records[0]["customer_email"] == "one@example.com"
    assert records[0]["tags"] == ["login", "password"]
    assert records[0]["metadata"]["source"] == "web_form"


def test_parse_csv_tickets_rejects_empty_file() -> None:
    with pytest.raises(ImportParseError, match="header row"):
        parse_csv_tickets("")


def test_parse_csv_tickets_rejects_header_only_file() -> None:
    with pytest.raises(ImportParseError, match="does not contain"):
        parse_csv_tickets("customer_id,customer_email\n")
