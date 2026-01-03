from typing import Dict, Optional
import os
import logging

from fingerprinting.parsing.language_detector import detect_language
from fingerprinting.parsing.treesitter_parser import TreeSitterParser

from fingerprinting.uast.uast_builder import UASTBuilder
from fingerprinting.uast.uast_compare import UASTComparator

logger = logging.getLogger(__name__)


class StructuralAgent:
    """
    StructuralAgent (UAST-based)

    - Builds UAST from Tree-sitter AST
    - Compares UAST subtrees
    - Language-agnostic
    - Runs ONLY for Top-K candidates
    """

    # --------------------------------------------------
    # Build UASTs for an entire repository
    # --------------------------------------------------
    def _build_repo_uast(self, repo_path: str):
        uast_roots = []

        for root, _, files in os.walk(repo_path):
            for file in files:
                file_path = os.path.join(root, file)

                lang = detect_language(file_path)
                if not lang:
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()

                    if not code.strip():
                        continue

                    tree = TreeSitterParser.parse_code(code, lang)
                    if not tree or not tree.root_node:
                        continue

                    uast_root = UASTBuilder.build(tree)
                    uast_roots.append(uast_root)

                except (UnicodeDecodeError, ValueError, RuntimeError) as e:
                    logger.debug(f"[STRUCT] Failed parsing {file_path}: {e}")
                    continue

        return uast_roots

    # --------------------------------------------------
    # Orchestrator entry point
    # --------------------------------------------------
    def run(
        self,
        input_repo_path: str,
        cand_repo_path: str,
        simhash_score: Optional[float] = None,
    ) -> Dict:
        """
        Compare structural similarity between two repositories.
        """

        # --------------------------------------------------
        # FAST PATH:
        # same directory + very high simhash → skip AST
        # --------------------------------------------------
        try:
            if simhash_score is not None and simhash_score >= 0.9:
                return {
                    "agent": "structural",
                    "score": 1.0,
                    "details": {
                        "reason": "high_simhash_skip_structure",
                        "simhash_score": simhash_score,
                    },
                }
        except OSError as e:
            logger.debug(f"[STRUCT] samefile check skipped: {e}")

        # --------------------------------------------------
        # Build UASTs
        # --------------------------------------------------
        input_uasts = self._build_repo_uast(input_repo_path)
        cand_uasts = self._build_repo_uast(cand_repo_path)

        logger.info(
            f"[STRUCT] input_uasts={len(input_uasts)} "
            f"candidate_uasts={len(cand_uasts)}"
        )

        if not input_uasts or not cand_uasts:
            return {
                "agent": "structural",
                "score": 0.0,
                "details": {
                    "reason": "no_uast_generated",
                    "input_uast_count": len(input_uasts),
                    "candidate_uast_count": len(cand_uasts),
                },
            }

        # --------------------------------------------------
        # Compare all UAST pairs (max similarity)
        # --------------------------------------------------
        scores = []
        for u1 in input_uasts:
            for u2 in cand_uasts:
                score = UASTComparator.similarity(u1, u2)
                scores.append(score)

        final_score = max(scores) if scores else 0.0

        return {
            "agent": "structural",
            "score": round(float(final_score), 4),
            "details": {
                "input_uast_count": len(input_uasts),
                "candidate_uast_count": len(cand_uasts),
                "comparison_pairs": len(scores),
            },
        }
