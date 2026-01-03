# agents/fingerprint_agent.py

import os
import hashlib
from typing import Dict, Any

from fingerprinting.simhash import (
    normalize_code,
    tokenize,
    compute_simhash,
    simhash_similarity,
)

from fingerprinting.winnowing import (
    winnow,
    jaccard_similarity,
)

SUPPORTED_EXT = (".py", ".java", ".js", ".ts", ".cpp", ".c")


import os
from typing import Dict, Any, Set

from fingerprinting.simhash import (
    normalize_code,
    tokenize,
    compute_simhash,
    simhash_similarity,
)

from fingerprinting.winnowing import (
    winnow,
    jaccard_similarity,
)

from storage.db import save_repository, save_fingerprint


SUPPORTED_EXT = (".py", ".java", ".js", ".ts", ".cpp", ".c")


class FingerprintAgent:
    """
    FingerprintAgent (DB-first, scalable)

    Responsibilities:
    1. Compute fingerprint ONCE for input repo
    2. Persist fingerprint to DB (learning step)
    3. Compare input fingerprint with DB fingerprints
    """

    # --------------------------------------------------
    # STEP 1: Compute input fingerprint (filesystem)
    # --------------------------------------------------
    def compute_input_fingerprint(self, repo_path: str) -> Dict[str, Any]:
        tokens = []

        for root, _, files in os.walk(repo_path):
            for f in files:
                if not f.lower().endswith(SUPPORTED_EXT):
                    continue

                file_path = os.path.join(root, f)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
                        code = fh.read()
                except Exception:
                    continue

                if not code.strip():
                    continue

                normalized = normalize_code(code)
                toks = tokenize(normalized)
                tokens.extend(toks)

        if not tokens:
            return {
                "simhash": 0,
                "winnowing": set(),
                "token_count": 0,
            }

        return {
            "simhash": compute_simhash(tokens),
            "winnowing": set(winnow(tokens)),
            "token_count": len(tokens),
        }

    # --------------------------------------------------
    # STEP 2: INGEST input repo into DB (CRITICAL)
    # --------------------------------------------------
    def ingest_repo(
        self,
        repo_url: str,
        repo_path: str,
    ) -> Dict[str, Any]:
        """
        Compute fingerprint and persist it to DB.
        This is what makes the system LEARN.
        """

        fp = self.compute_input_fingerprint(repo_path)

        if fp["token_count"] == 0:
            return fp

        # Using simhash as content identity (good enough here)
        content_hash = str(fp["simhash"])

        repo_id = save_repository(repo_url, content_hash)

        # ---- save simhash fingerprint ----
        save_fingerprint(
            repo_id=repo_id,
            agent="simhash",
            score=1.0,
            extra_data={   # ✅ FIXED
                "simhash": str(fp["simhash"]),
                "token_count": fp["token_count"],
            },
        )

        # ---- save winnowing fingerprint ----
        save_fingerprint(
            repo_id=repo_id,
            agent="winnowing",
            score=1.0,
            extra_data={   # ✅ FIXED
                "winnowing": list(fp["winnowing"]),
                "token_count": fp["token_count"],
            },
        )

        return fp

    # --------------------------------------------------
    # STEP 3: Compare with DB fingerprints (NO FS)
    # --------------------------------------------------
    def compare_with_db(
        self,
        input_fp: Dict[str, Any],
        db_fp: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        db_fp must contain:
        {
            "repo_url": str,
            "simhash": int,
            "winnowing": Set[int],
            "token_count": int
        }
        """

        simhash_score = simhash_similarity(
            input_fp["simhash"],
            db_fp["simhash"],
        )

        winnowing_score = jaccard_similarity(
            input_fp["winnowing"],
            set(db_fp["winnowing"]),
        )

        combined = (simhash_score + winnowing_score) / 2.0

        return {
            "agent": "fingerprint",
            "simhash_score": round(simhash_score, 4),
            "winnowing_score": round(winnowing_score, 4),
            "score": round(combined, 4),
            "details": {
                "candidate_repo": db_fp["repo_url"],
                "input_tokens": input_fp["token_count"],
                "candidate_tokens": db_fp["token_count"],
            },
        }
