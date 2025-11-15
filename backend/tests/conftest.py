import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

@pytest.fixture
def tmp_repo(tmp_path):
    # create a tiny fake repo
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / "a.py").write_text("print('hello')\n# comment\n")
    (repo_dir / "b.py").write_text("def foo():\n    return 1\n")
    # create .git/logs/HEAD to satisfy contributor agent
    git_dir = repo_dir / ".git" / "logs"
    git_dir.mkdir(parents=True)
    (git_dir / "HEAD").write_text("commitlog sample")
    return str(repo_dir)
