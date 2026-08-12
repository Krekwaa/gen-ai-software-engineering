import json
from decimal import Decimal

import pytest

from pipeline.common import account_reference, audit, envelope, parse_amount, parse_timestamp, write_json


def test_common_value_helpers():
    assert parse_amount("1.20") == Decimal("1.20")
    assert parse_timestamp("2026-01-01T00:00:00Z").tzinfo is not None
    assert account_reference("secret") == account_reference("secret")
    assert account_reference("secret") != "secret"


@pytest.mark.parametrize("value", ["NaN", "Infinity", object()])
def test_parse_amount_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        parse_amount(value)


@pytest.mark.parametrize("value", [None, "not-a-date", "2026-01-01T00:00:00"])
def test_parse_timestamp_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        parse_timestamp(value)


def test_file_envelope_and_audit_helpers(tmp_path):
    message = envelope({"transaction_id": "T1"}, "a", "b")
    assert message["source_stage"] == "a" and message["target_stage"] == "b"
    target = tmp_path / "nested" / "record.json"
    write_json(target, message)
    assert json.loads(target.read_text(encoding="utf-8"))["message_id"]
    log = tmp_path / "audit" / "events.jsonl"
    audit(log, "validator", "T1", "validated")
    assert json.loads(log.read_text(encoding="utf-8"))["outcome"] == "validated"

