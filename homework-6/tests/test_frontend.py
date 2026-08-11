import json

from frontend import app as dashboard


def test_load_summary_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(dashboard, "RESULTS_DIR", tmp_path)
    assert dashboard.load_summary()["total"] == 0


def test_load_summary_and_dashboard(tmp_path, monkeypatch):
    (tmp_path / "summary.json").write_text(json.dumps({"total": 2}), encoding="utf-8")
    monkeypatch.setattr(dashboard, "RESULTS_DIR", tmp_path)
    assert dashboard.api_results() == {"total": 2}
    assert "Transaction Pipeline" in dashboard.dashboard()


def test_api_run_uses_project_input(tmp_path, monkeypatch):
    source = tmp_path / "sample-transactions.json"
    source.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(dashboard, "PROJECT_ROOT", tmp_path)
    result = dashboard.api_run()
    assert result["total"] == 0
