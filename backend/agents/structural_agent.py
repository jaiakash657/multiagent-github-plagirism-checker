from typing import Tuple, Dict
import os

class StructuralAgent:
    def analyze(self, repo_path: str, depth: int = 1) -> Tuple[float, Dict]:
        """
        Structural checks: file counts, average file length, suspicious identical filenames, deep nesting.
        """
        file_count = 0
        total_lines = 0
        max_depth = 0
        name_counts = {}
        for root, _, files in os.walk(repo_path):
            depth_level = root.count(os.sep) - repo_path.count(os.sep)
            max_depth = max(max_depth, depth_level)
            for f in files:
                file_count += 1
                name_counts[f] = name_counts.get(f, 0) + 1
                try:
                    with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fh:
                        total_lines += sum(1 for _ in fh)
                except Exception:
                    continue
        avg_lines = total_lines / (file_count or 1)
        dup_names = sum(1 for v in name_counts.values() if v > 1)
        # heuristic: more duplicate names and very large avg_lines may increase structural similarity suspicion
        score = min(1.0, (dup_names * 0.3) + (avg_lines / 1000.0) + (max_depth * 0.05))
        return score, {"file_count": file_count, "avg_lines": avg_lines, "dup_names": dup_names, "max_depth": max_depth}
