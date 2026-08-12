import json

from pipeline import validator
from pipeline.validator import process_transaction


def valid_record():
    return {"transaction_id":"T1","timestamp":"2026-01-01T12:00:00Z","source_account":"A","destination_account":"B","amount":"10.00","currency":"USD","transaction_type":"transfer"}


def test_accepts_valid_transaction():
    result = process_transaction(valid_record())
    assert result["status"] == "validated"
    assert result["validation"] == {"valid": True, "reasons": []}


def test_rejects_missing_invalid_amount_currency_and_timestamp():
    record = valid_record()
    record.pop("destination_account")
    record.update(amount="-2", currency="XYZ", timestamp="yesterday")
    result = process_transaction(record)
    assert result["status"] == "rejected"
    assert len(result["validation"]["reasons"]) == 4


def test_rejects_non_decimal_and_empty_identifier():
    record = valid_record()
    record.update(amount="not-money", transaction_id="")
    result = process_transaction(record)
    assert not result["validation"]["valid"]


def test_dry_run_and_cli_summary(tmp_path, monkeypatch, capsys):
    source = tmp_path / "transactions.json"
    source.write_text(json.dumps([valid_record()]), encoding="utf-8")
    assert validator.dry_run(source)[0]["status"] == "validated"
    monkeypatch.setattr("sys.argv", ["validator", "--dry-run", "--input", str(source)])
    assert validator.main() == 0
    assert "Valid: 1" in capsys.readouterr().out
