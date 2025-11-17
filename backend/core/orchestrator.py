# core/orchestrator.py (only revised run_multiple shown)
from agents.lexical_agent import LexicalAgent
from agents.structural_agent import StructuralAgent
from agents.semantic_agent import SemanticAgent
from agents.contributor_agent import ContributorAgent
from agents.fingerprint_agent import FingerprintAgent
from agents.simhash_agent import SimHashAgent
from agents.winnowing_agent import WinnowingAgent

from core.aggregator import aggregate_multiple_repos

class Orchestrator:
    def __init__(self):
        # keep order: fast agents first
        self.simhash_agent = SimHashAgent()
        self.winnow_agent = WinnowingAgent()
        self.other_agents = [
            LexicalAgent(),
            StructuralAgent(),
            SemanticAgent(),
            ContributorAgent(),
            FingerprintAgent(),
        ]

    def run_multiple(self, repo_paths: dict, max_simhash_hamming: int = 6, winnow_threshold: float = 0.05):
        """
        repo_paths = { repo_url: local_path, ... }
        Workflow:
          1. Compute input simhash (and ensure in DB)
          2. Find DB candidates by simhash proximity
          3. For each candidate (plus any seed candidates in repo_paths), run winnowing
          4. If winnowing score > threshold, run other agents on that candidate
        """
        # pick one as input (first key) - usually the repo user provided
        input_repo_url = list(repo_paths.keys())[0]
        input_path = repo_paths[input_repo_url]

        # 1. quick candidate list using SimHash DB scan
        sim_candidates = self.simhash_agent.fast_candidates_by_simhash(input_repo_url, input_path, max_hamming=max_simhash_hamming)
        # ensure we include repo_paths keys (cloned candidates)
        candidate_urls = set(sim_candidates) | set(repo_paths.keys())

        aggregated_results = {}

        # for every candidate, run simhash compare immediately (cheap)
        for cand_url in candidate_urls:
            cand_path = repo_paths.get(cand_url)  # may be None if not cloned locally
            if not cand_path:
                # If not cloned locally, skip or clone if you prefer
                continue

            sim_res = self.simhash_agent.compare(input_repo_url, input_path, cand_url, cand_path)
            # early reject if simhash zero similarity
            if sim_res["score"] <= 0.01:
                # still store simhash result
                aggregated_results[cand_url] = {"agent_scores": [sim_res]}
                continue

            # run winnowing next
            win_res = self.winnow_agent.compare(input_repo_url, input_path, cand_url, cand_path)
            agent_scores = [sim_res, win_res]

            # if winnowing passes threshold, run other heavier agents
            if win_res["score"] >= winnow_threshold:
                for agent in self.other_agents:
                    try:
                        ag_res = agent.run(cand_path) if hasattr(agent, "run") else agent.run(cand_path)
                        agent_scores.append(ag_res)
                    except Exception:
                        # ignore agent failure for now
                        pass

            aggregated_results[cand_url] = {"agent_scores": agent_scores}

        # Convert to the format expected by aggregate_multiple_repos
        repo_results = {}
        for repo_url, d in aggregated_results.items():
            repo_results[repo_url] = d["agent_scores"]

        output = aggregate_multiple_repos(repo_results)
        return output
