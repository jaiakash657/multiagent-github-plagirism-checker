from typing import Tuple, Dict
import os
import re

class LexicalAgent:
    def analyze(self, repo_path: str, depth: int = 1) -> Tuple[float, Dict]:
        """
        Naive lexical similarity: count repeated tokens, basic frequency-based heuristic.
        Placeholder — replace with your real lexical checks.
        """
        tokens = {}
        for root, _, files in os.walk(repo_path):
            for f in files:
                if f.endswith((".py", ".java", ".js")):
                    path = os.path.join(root, f)
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                            text = fh.read()
                        words = re.findall(r"\w+", text)
                        for w in words:
                            tokens[w] = tokens.get(w, 0) + 1
                    except Exception:
                        continue
        # simplistic score: proportion of repeated tokens > threshold
        repeated = sum(1 for v in tokens.values() if v > 3)
        score = min(1.0, repeated / (len(tokens) + 1))
        return score, {"repeated_tokens": repeated, "unique_tokens": len(tokens)}
