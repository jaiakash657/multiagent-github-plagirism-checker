# agents/fingerprint_agent.py

import os
import hashlib

from fingerprinting.simhash import (
    normalize_code,
    tokenize,
    compute_simhash,
    simhash_similarity,
)
from fingerprinting.winnowing import (
    winnow,
    jaccard_from_fingerprints,
)

from storage.db import save_repository, save_fingerprint

SUPPORTED_EXT = (".py", ".java", ".js")


class FingerprintAgent:
    """
    FingerprintAgent:
    - Repo-level SimHash (coarse similarity)
    - Repo-level Winnowing + Jaccard (fine similarity)
    - NO URL shortcuts, NO forced identity
    """

    # ------------------------------
    # Token collection
    # ------------------------------
    def _collect_tokens(self, repo_path: str):
        tokens = []
        file_blobs = []

        for root, _, files in os.walk(repo_path):
            for f in files:
                if f.endswith(SUPPORTED_EXT):
                    path = os.path.join(root, f)
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                            code = fh.read()
                        norm = normalize_code(code)
                        toks = tokenize(norm)
                        tokens.extend(toks)
                        file_blobs.append((path, norm))
                    except Exception:
                        continue

        return tokens, file_blobs

    # ------------------------------
    # Content hash (storage only)
    # ------------------------------
    def _compute_content_hash(self, file_blobs):
        h = hashlib.sha256()
        for path, content in sorted(file_blobs, key=lambda x: x[0]):
            h.update(path.encode())
            h.update(content.encode())
        return h.hexdigest()

    # ------------------------------
    # Compare
    # ------------------------------
    def compare(
        self,
        input_repo_url: str,
        input_path: str,
        cand_repo_url: str,
        cand_path: str,
    ) -> dict:

        # 1️⃣ Collect tokens
        tokens_a, blobs_a = self._collect_tokens(input_path)
        tokens_b, blobs_b = self._collect_tokens(cand_path)

        if not tokens_a or not tokens_b:
            return {
                "agent": "fingerprint",
                "score": 0.0,
            }

        # 2️⃣ Compute content hash (for DB, not scoring)
        hash_a = self._compute_content_hash(blobs_a)
        save_repository(input_repo_url, hash_a)

        # 3️⃣ SimHash (coarse similarity)
        simhash_a = compute_simhash(tokens_a)
        simhash_b = compute_simhash(tokens_b)
        simhash_score = simhash_similarity(simhash_a, simhash_b)

        # 4️⃣ Winnowing (fine similarity)
        fp_a = winnow(tokens_a)
        fp_b = winnow(tokens_b)
        winnowing_score = jaccard_from_fingerprints(fp_a, fp_b)

        # 5️⃣ Combined score
        combined_score = (simhash_score + winnowing_score) / 2.0

        # 6️⃣ Persist fingerprints
        save_fingerprint(
            repo_id=save_repository(input_repo_url, hash_a),
            agent="simhash",
            score=simhash_score,
            metadata={
                "simhash": str(simhash_a),
                "token_count": len(tokens_a),
            },
        )

        save_fingerprint(
            repo_id=save_repository(input_repo_url, hash_a),
            agent="winnowing",
            score=winnowing_score,
            metadata={
                "fingerprints": len(fp_a),
                "token_count": len(tokens_a),
            },
        )

        return {
            "agent": "fingerprint",
            "simhash_score": simhash_score,
            "winnowing_score": winnowing_score,
            "score": combined_score,
            "details": {
                "input_repo": input_repo_url,
                "candidate_repo": cand_repo_url,
                "token_count_a": len(tokens_a),
                "token_count_b": len(tokens_b),
            },
        }
