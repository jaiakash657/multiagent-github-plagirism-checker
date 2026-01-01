from agents.fingerprint_agent import FingerprintAgent
from agents.structural_agent import StructuralAgent
from agents.semantic_agent import SemanticAgent
from agents.contributor_agent import ContributorAgent

from core.aggregator import aggregate_multiple_repos


class Orchestrator:
    def __init__(self):
        # fast filter first
        self.fingerprint_agent = FingerprintAgent()

        # heavier agents later
        self.other_agents = [
            StructuralAgent(),
            SemanticAgent(),
            ContributorAgent(),
        ]

    def run_multiple(
        self,
        repo_paths: dict,
        simhash_threshold: float = 0.01,
        winnow_threshold: float = 0.05,
    ):
        """
        repo_paths = { repo_url: local_path }

        Flow:
          1. FingerprintAgent → SimHash + Winnowing
          2. If candidate passes thresholds → run heavier agents
          3. Aggregate scores
        """

        input_repo_url = list(repo_paths.keys())[0]
        input_path = repo_paths[input_repo_url]

        aggregated_results = {}

        for cand_url, cand_path in repo_paths.items():

            # 1️⃣ fingerprint stage (ALWAYS RUN)
            fp_res = self.fingerprint_agent.compare(
                input_repo_url,
                input_path,
                cand_url,
                cand_path,
            )

            agent_scores = [fp_res]

            # early prune (but allow self-comparison)
            if fp_res["simhash_score"] < simhash_threshold:
                aggregated_results[cand_url] = agent_scores
                continue

            if fp_res["winnowing_score"] >= winnow_threshold:
                for agent in self.other_agents:
                    try:
                        agent_scores.append(agent.run(input_path, cand_path))
                    except Exception:
                        pass

            aggregated_results[cand_url] = agent_scores


        return aggregate_multiple_repos(aggregated_results)
