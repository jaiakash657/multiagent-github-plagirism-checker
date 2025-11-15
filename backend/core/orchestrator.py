from agents.lexical_agent import LexicalAgent
from agents.structural_agent import StructuralAgent
from agents.semantic_agent import SemanticAgent
from agents.contributor_agent import ContributorAgent
from agents.fingerprint_agent import FingerprintAgent

from core.aggregator import aggregate_results


class Orchestrator:

    def __init__(self):
        self.agents = [
            LexicalAgent(),
            StructuralAgent(),
            SemanticAgent(),
            ContributorAgent(),
            FingerprintAgent(),
        ]

    def run(self, repo_path: str):
        """
        Runs all agents and returns aggregated result.
        """
        results = []

        for agent in self.agents:
            agent_result = agent.run(repo_path)
            results.append(agent_result)

        # Combine results into single final score
        return aggregate_results(results)
