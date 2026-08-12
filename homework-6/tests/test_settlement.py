from pipeline.settlement import process_transaction


def test_settles_low_risk_and_rounds_amount():
    result = process_transaction({"amount":"10.125","status":"risk_scored","fraud":{"risk_level":"low"}})
    assert result["amount"] == "10.13"
    assert result["status"] == "settled"


def test_holds_high_risk():
    result = process_transaction({"amount":"10","status":"fraud_review","fraud":{"risk_level":"high"}})
    assert result["status"] == "held_for_review"
    assert result["settlement"]["reason"] == "high_fraud_risk"


def test_does_not_settle_rejected_record():
    result = process_transaction({"status":"rejected"})
    assert result["settlement"]["outcome"] == "not_attempted"

