from typing import Tuple, Dict
import os
import json
from datetime import datetime

class ContributorAgent:
    def analyze(self, repo_path: str, depth: int = 1) -> Tuple[float, Dict]:
        """
        Check commit history/author patterns — placeholder: tries to read .git/logs HEAD if present
        """
        gitlogs = os.path.join(repo_path, ".git", "logs", "HEAD")
        if not os.path.exists(gitlogs):
            return 0.0, {"reason": "no_git_logs"}
        authors = {}
        try:
            with open(gitlogs, "r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    parts = line.strip().split()
                    # rough parsing: last token might contain author info in some formats: skip robust parsing
                    for token in parts:
                        if "@" in token and "<" not in token:
                            authors[token] = authors.get(token, 0) + 1
            n_authors = len(authors)
            score = min(1.0, (1.0 / (n_authors + 1)) if n_authors > 0 else 0.0)
            return score, {"n_authors": n_authors, "sample_authors": list(authors.keys())[:5]}
        except Exception as e:
            return 0.0, {"error": str(e)}
