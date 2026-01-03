import logging

from agents.fingerprint_agent import FingerprintAgent
from agents.structural_agent import StructuralAgent
from agents.semantic_agent import SemanticAgent
from agents.contributor_agent import ContributorAgent

from core.aggregator import aggregate_multiple_repos

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Orchestrator responsibilities:
    1. Ingest input repo (fingerprint → DB)
    2. Rank DB repos using fingerprint similarity (NO filesystem)
    3. Select TOP-K candidates
    4. Run deep agents ONLY if thresholds pass
    5. ALWAYS return fingerprint results
    """

    def __init__(self):
        self.fingerprint_agent = FingerprintAgent()
        self.structural_agent = StructuralAgent()

        self.heavy_agents = [
            SemanticAgent(),
            ContributorAgent(),
        ]

    def run_multiple(
        self,
        input_repo_url: str,
        input_path: str,
        repo_paths: dict,        # {repo_url: local_path}
        db_candidates: list,     # [{repo_url, simhash, winnowing, token_count}]
        top_k: int = 3,
        simhash_threshold: float = 0.01,
        winnow_threshold: float = 0.05,
    ):
        # --------------------------------------------------
        # PHASE 0: Ingest input repo (learning step)
        # --------------------------------------------------
        input_fp = self.fingerprint_agent.ingest_repo(
            input_repo_url,
            input_path,
        )

        # --------------------------------------------------
        # PHASE 1: Fingerprint-only ranking (DB only)
        # --------------------------------------------------
        ranked = []

        for cand in db_candidates:
            try:
                fp_score = self.fingerprint_agent.compare_with_db(
                    input_fp,
                    cand,
                )
            except Exception:
                logger.exception(f"[FP ERROR] {cand.get('repo_url')}")
                continue

            ranked.append({
                "repo_url": cand["repo_url"],
                "fp": fp_score,
            })

        ranked.sort(
            key=lambda x: (
                x["fp"].get("simhash_score", 0.0)
                + x["fp"].get("winnowing_score", 0.0)
            ),
            reverse=True,
        )

        top_candidates = ranked[:top_k]

        logger.info(
            f"[ORCH] TOP-{top_k} fingerprint candidates: "
            f"{[c['repo_url'] for c in top_candidates]}"
        )

        # --------------------------------------------------
        # PHASE 2: Conditional deep analysis
        # --------------------------------------------------
        aggregated_results = {}

        for item in top_candidates:
            cand_url = item["repo_url"]
            fp_res = item["fp"]

            # 🔑 ALWAYS include fingerprint result
            agent_scores = [fp_res]

            # Skip deep analysis for self repo
            if cand_url == input_repo_url:
                aggregated_results[cand_url] = agent_scores
                continue

            cand_path = repo_paths.get(cand_url)

            # -------------------------------
            # Structural agent (AST)
            # -------------------------------
            if (
                cand_path
                and fp_res["simhash_score"] >= simhash_threshold
            ):
                try:
                    agent_scores.append(
                        self.structural_agent.run(
                            input_path,
                            cand_path,
                            simhash_score=fp_res["simhash_score"],
                        )
                    )
                except Exception:
                    logger.exception(f"[AST ERROR] {cand_url}")

            # -------------------------------
            # Heavy agents (semantic, contributor)
            # -------------------------------
            if (
                cand_path
                and fp_res["winnowing_score"] >= winnow_threshold
            ):
                for agent in self.heavy_agents:
                    try:
                        agent_scores.append(
                            agent.run(input_path, cand_path)
                        )
                    except Exception:
                        logger.exception(
                            f"[AGENT ERROR] {agent.__class__.__name__} {cand_url}"
                        )

            aggregated_results[cand_url] = agent_scores

        # --------------------------------------------------
        # FINAL: Aggregate + normalize scores
        # --------------------------------------------------
        return aggregate_multiple_repos(aggregated_results)
