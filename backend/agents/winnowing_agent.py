# agents/winnowing_agent.py
from fingerprinting.manager import compute_fingerprints_for_repo
from fingerprinting.winnowing import jaccard_from_fingerprints
from storage.db import load_fingerprints, save_fingerprints, init_db

class WinnowingAgent:
    def __init__(self):
        self.name = "winnowing"
        init_db()

    def ensure_fp(self, repo_url: str, local_path: str):
        existing = load_fingerprints(repo_url)
        if existing:
            return existing
        fp = compute_fingerprints_for_repo(local_path)
        from storage.db import save_fingerprints
        save_fingerprints(repo_url, fp["simhash"], fp["winnowing"], fp["token_count"], metadata={"local_path": local_path})
        return {"repo_url": repo_url, **fp}

    def compare(self, input_repo_url: str, input_local_path: str, candidate_repo_url: str, candidate_local_path: str):
        in_fp = self.ensure_fp(input_repo_url, input_local_path)
        cand_fp = self.ensure_fp(candidate_repo_url, candidate_local_path)
        score = jaccard_from_fingerprints(in_fp["winnowing"], cand_fp["winnowing"])
        matching = len(set(h for h,_ in in_fp["winnowing"]) & set(h for h,_ in cand_fp["winnowing"]))
        total = max(1, len(set(h for h,_ in in_fp["winnowing"]) | set(h for h,_ in cand_fp["winnowing"])))
        return {
            "agent": self.name,
            "score": float(score),
            "details": {
                "matching_fingerprints": matching,
                "union_count": total,
                "similarity": float(score)
            }
        }
