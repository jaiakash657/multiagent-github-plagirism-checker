from agents.lexical_agent import LexicalAgent
from agents.semantic_agent import SemanticAgent
from agents.structural_agent import StructuralAgent
from agents.fingerprint_agent import FingerprintAgent
from agents.contributor_agent import ContributorAgent
import os

def test_lexical_on_small(tmp_path):
    p = tmp_path / "r"
    p.mkdir()
    (p / "t.py").write_text("a a a a b c d e f g")
    agent = LexicalAgent()
    score, details = agent.analyze(str(p))
    assert 0.0 <= score <= 1.0

def test_structural(tmp_path):
    p = tmp_path / "r"
    p.mkdir()
    (p / "one.py").write_text("print(1)\n")
    (p / "two.py").write_text("print(2)\n")
    agent = StructuralAgent()
    s, d = agent.analyze(str(p))
    assert "file_count" in d

def test_fingerprint(tmp_path):
    p = tmp_path / "r"
    p.mkdir()
    content = "x=1\n"
    (p / "a.py").write_text(content)
    (p / "b.py").write_text(content)
    agent = FingerprintAgent()
    s, d = agent.analyze(str(p))
    assert s >= 0.0

def test_contributor(tmp_path):
    p = tmp_path / "r"
    p.mkdir()
    git_dir = p / ".git" / "logs"
    git_dir.mkdir(parents=True)
    (git_dir / "HEAD").write_text("some log with author@domain")
    agent = ContributorAgent()
    s, d = agent.analyze(str(p))
    assert isinstance(d, dict)
