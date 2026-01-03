from typing import Tuple, Dict
import os
import subprocess
from collections import Counter


class ContributorAgent:
    """
    Contributor analysis based on git commit history.
    Produces a weak plagiarism signal based on authorship dominance.
    """

    def analyze(self, repo_path: str) -> Tuple[float, Dict]:
        git_dir = os.path.join(repo_path, ".git")
        if not os.path.exists(git_dir):
            return 0.0, {"reason": "no_git_repo"}

        try:
            result = subprocess.run(
                ["git", "-C", repo_path, "log", "--pretty=format:%ae"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return 0.0, {"reason": "git_log_failed"}

            authors = [
                line.strip()
                for line in result.stdout.splitlines()
                if line.strip()
            ]

            if not authors:
                return 0.0, {"reason": "no_authors"}

            counts = Counter(authors)
            total_commits = sum(counts.values())
            dominant_author, dominant_count = counts.most_common(1)[0]

            dominance_ratio = dominant_count / total_commits

            # Higher dominance → higher plagiarism suspicion
            score = dominance_ratio

            return score, {
                "total_commits": total_commits,
                "n_authors": len(counts),
                "dominant_author": dominant_author,
                "dominance_ratio": round(dominance_ratio, 3),
                "sample_authors": list(counts.keys())[:5],
            }

        except Exception as e:
            return 0.0, {"error": str(e)}

    def run(self, input_repo_path: str, cand_repo_path: str) -> Dict:
        """
        Orchestrator-compatible entry point.
        Contributor signal is computed on the candidate repo.
        """
        score, details = self.analyze(cand_repo_path)
        return {
            "agent": "contributor",
            "score": float(score),
            "details": details,
        }
