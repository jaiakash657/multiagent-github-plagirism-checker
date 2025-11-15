from core.orchestrator import orchestrate_analysis
import tempfile
import os

def test_orchestrator_with_empty_repo(tmp_path, monkeypatch):
    p = tmp_path / "repo"
    p.mkdir()
    results = orchestrate_analysis(str(p))
    assert isinstance(results, list)
