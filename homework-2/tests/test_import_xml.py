import pytest

from src.backend.app.importers import ImportParseError, parse_xml_tickets


def test_parse_xml_tickets_returns_records() -> None:
    records = parse_xml_tickets(
        """
        <tickets>
          <ticket>
            <customer_id>cust-001</customer_id>
            <customer_email>one@example.com</customer_email>
            <customer_name>One User</customer_name>
            <subject>Feature idea</subject>
            <description>I have a suggestion for improving reports.</description>
            <category>feature_request</category>
            <priority>low</priority>
            <tags>
              <tag>reports</tag>
              <tag>suggestion</tag>
            </tags>
            <metadata>
              <source>email</source>
              <device_type>desktop</device_type>
            </metadata>
          </ticket>
        </tickets>
        """
    )

    assert len(records) == 1
    assert records[0]["category"] == "feature_request"
    assert records[0]["tags"] == ["reports", "suggestion"]
    assert records[0]["metadata"]["source"] == "email"


def test_parse_xml_tickets_accepts_single_ticket_root() -> None:
    records = parse_xml_tickets(
        """
        <ticket>
          <customer_id>cust-002</customer_id>
          <customer_email>two@example.com</customer_email>
          <customer_name>Two User</customer_name>
          <subject>Password issue</subject>
          <description>I cannot access my account with 2FA enabled.</description>
        </ticket>
        """
    )

    assert records[0]["customer_id"] == "cust-002"


def test_parse_xml_tickets_rejects_malformed_xml() -> None:
    with pytest.raises(ImportParseError, match="Malformed XML"):
        parse_xml_tickets("<tickets><ticket></tickets>")


def test_parse_xml_tickets_rejects_missing_ticket_elements() -> None:
    with pytest.raises(ImportParseError, match="does not contain"):
        parse_xml_tickets("<items></items>")
