# agents/simhash_agent.py
from fingerprinting.manager import compute_fingerprints_for_repo
from storage.db import load_fingerprints, save_fingerprints, query_simhash_candidates, init_db
import os

class SimHashAgent:
    def __init__(self):
        self.name = "simhash"
        init_db()

    def ensure_repo_fingerprints(self, repo_url: str, local_path: str):
        # repo_url is used as DB key; we store fingerprints for local_path under repo_url
        existing = load_fingerprints(repo_url)
        if existing:
            return existing
        fp = compute_fingerprints_for_repo(local_path)
        save_fingerprints(repo_url, fp["simhash"], fp["winnowing"], fp["token_count"], metadata={"local_path": local_path})
        return {
            "repo_url": repo_url,
            **fp
        }

    def compare(self, input_repo_url: str, input_local_path: str, candidate_repo_url: str, candidate_local_path: str):
        in_fp = self.ensure_repo_fingerprints(input_repo_url, input_local_path)
        cand_fp = self.ensure_repo_fingerprints(candidate_repo_url, candidate_local_path)
        from fingerprinting.simhash import simhash_similarity, hamming_distance
        sim = simhash_similarity(in_fp["simhash"], cand_fp["simhash"])
        dist = hamming_distance(in_fp["simhash"], cand_fp["simhash"])
        return {
            "agent": self.name,
            "score": sim,
            "details": {
                "input_hash": in_fp["simhash"],
                "candidate_hash": cand_fp["simhash"],
                "hamming_distance": dist,
                "similarity": sim
            }
        }

    def fast_candidates_by_simhash(self, input_repo_url: str, input_local_path: str, max_hamming: int = 6, limit: int = 50):
        """Return candidate repo_url list from DB based on simhash proximity."""
        in_fp = self.ensure_repo_fingerprints(input_repo_url, input_local_path)
        return query_simhash_candidates(in_fp["simhash"], max_hamming=max_hamming, limit=limit)
