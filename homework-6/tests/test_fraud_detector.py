from pipeline.fraud_detector import process_transaction


def record(amount="100.00", timestamp="2026-01-01T12:00:00Z", country="US", currency="USD"):
    return {"transaction_id":"T1","amount":amount,"timestamp":timestamp,"currency":currency,"metadata":{"country":country},"status":"validated"}


def test_low_risk_transaction():
    result = process_transaction(record())
    assert result["fraud"]["risk_score"] == 0
    assert result["status"] == "risk_scored"


def test_very_high_value_is_held():
    result = process_transaction(record(amount="50000"))
    assert result["fraud"]["risk_level"] == "high"
    assert "very_high_value" in result["fraud"]["indicators"]


def test_high_value_is_medium_risk():
    result = process_transaction(record(amount="10001"))
    assert result["fraud"]["risk_score"] == 45
    assert result["fraud"]["risk_level"] == "medium"


def test_combined_indicators_and_score_cap():
    result = process_transaction(record(amount="50001", timestamp="2026-01-01T02:00:00Z", country="CA"))
    assert result["fraud"]["risk_score"] == 100
    assert set(result["fraud"]["indicators"]) == {"very_high_value", "unusual_time", "cross_border"}


def test_rejected_record_bypasses_scoring():
    item = record()
    item["status"] = "rejected"
    assert process_transaction(item) == item
