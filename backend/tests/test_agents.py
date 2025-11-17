from agents.lexical_agent import LexicalAgent
from agents.structural_agent import StructuralAgent
from agents.semantic_agent import SemanticAgent
from agents.fingerprint_agent import FingerprintAgent
from agents.contributor_agent import ContributorAgent


def test_lexical_agent(temp_repo):
    agent = LexicalAgent()
    result = agent.run(temp_repo)
    assert "score" in result
    assert result["agent"] == "LexicalAgent"


def test_structural_agent(temp_repo):
    agent = StructuralAgent()
    result = agent.run(temp_repo)
    assert "score" in result


def test_semantic_agent(temp_repo):
    agent = SemanticAgent()
    result = agent.run(temp_repo)
    assert "score" in result


def test_fingerprint_agent(temp_repo):
    agent = FingerprintAgent()
    result = agent.run(temp_repo)
    assert "score" in result


def test_contributor_agent():
    agent = ContributorAgent()
    result = agent.run("dummy/path")
    assert "score" in result
