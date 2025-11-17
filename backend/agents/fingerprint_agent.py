from typing import Tuple, Dict
import hashlib
import os

class FingerprintAgent:
    def _file_hash(self, path):
        h = hashlib.sha256()
        try:
            with open(path, "rb") as fh:
                while True:
                    chunk = fh.read(8192)
                    if not chunk:
                        break
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return None

    def analyze(self, repo_path: str, depth: int = 1) -> Tuple[float, Dict]:
        hashes = {}
        for root, _, files in os.walk(repo_path):
            for f in files:
                if f.endswith((".py", ".java", ".js")):
                    path = os.path.join(root, f)
                    hs = self._file_hash(path)
                    if hs:
                        hashes.setdefault(hs, []).append(path)

        duplicate_buckets = [v for v in hashes.values() if len(v) > 1]
        dup_count = sum(len(b) for b in duplicate_buckets)
        total = sum(len(v) for v in hashes.values()) or 1

        score = min(1.0, dup_count / total)

        return score, {
            "duplicate_files": dup_count,
            "total_files": total,
            "buckets": duplicate_buckets[:10]
        }

    def run(self, repo_path: str) -> Dict:
        """
        Orchestrator-compatible wrapper.
        """
        score, details = self.analyze(repo_path)
        return {
            "agent": "fingerprint",
            "score": score,
            "details": details
        }
