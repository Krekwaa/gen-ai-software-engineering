import json

import orchestrator
from orchestrator import prepare_directories, run_pipeline


def test_full_pipeline_isolated_from_project_shared(tmp_path):
    records = [
        {"transaction_id":"OK1","timestamp":"2026-01-01T12:00:00Z","source_account":"SECRET-A","destination_account":"SECRET-B","amount":"10.00","currency":"USD","transaction_type":"transfer","description":"private"},
        {"transaction_id":"BAD1","timestamp":"2026-01-01T12:00:00Z","source_account":"A","destination_account":"B","amount":"-1","currency":"USD","transaction_type":"transfer"},
    ]
    source = tmp_path / "input.json"
    source.write_text(json.dumps(records), encoding="utf-8")
    summary = run_pipeline(source, tmp_path)
    assert summary["status_counts"] == {"rejected": 1, "settled": 1}
    assert len(list((tmp_path / "shared/results").glob("*.json"))) == 3
    output = (tmp_path / "shared/results/OK1.json").read_text(encoding="utf-8")
    assert "SECRET-A" not in output and "private" not in output
    assert not list((tmp_path / "shared/processing").iterdir())


def test_pipeline_requires_array_input(tmp_path):
    source = tmp_path / "input.json"
    source.write_text("{}", encoding="utf-8")
    try:
        run_pipeline(source, tmp_path)
    except ValueError as exc:
        assert "JSON array" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_prepare_without_clearing_preserves_file(tmp_path):
    paths = prepare_directories(tmp_path)
    marker = paths["input"] / "keep.txt"
    marker.write_text("keep", encoding="utf-8")
    prepare_directories(tmp_path, clear=False)
    assert marker.exists()


def test_orchestrator_cli(tmp_path, monkeypatch, capsys):
    source = tmp_path / "input.json"
    source.write_text("[]", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["orchestrator", "--input", str(source), "--root", str(tmp_path)])
    assert orchestrator.main() == 0
    assert "Processed: 0" in capsys.readouterr().out
