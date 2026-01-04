import logging

from agents.fingerprint_agent import FingerprintAgent
from agents.structural_agent import StructuralAgent
from agents.semantic_agent import SemanticAgent
from agents.contributor_agent import ContributorAgent

from core.aggregator import aggregate_multiple_repos

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Orchestrator Responsibilities

    1. Ingest input repo (fingerprint → DB)
    2. Rank DB repos using fingerprint similarity
    3. Select TOP-K candidates
    4. Run agents conditionally based on thresholds
    """

    def __init__(self):
        self.fingerprint_agent = FingerprintAgent()
        self.structural_agent = StructuralAgent()
        self.semantic_agent = SemanticAgent()
        self.contributor_agent = ContributorAgent()

    def run_multiple(
        self,
        input_repo_url: str,
        input_path: str,
        repo_paths: dict,        # {repo_url: local_path}
        db_candidates: list,     # [{repo_url, simhash, winnowing, token_count}]
        top_k: int = 3,
        simhash_threshold: float = 0.05,
        winnowing_threshold: float = 0.05,
        force_heavy: bool = False,
    ):
        # --------------------------------------------------
        # PHASE 0: Ingest input repo
        # --------------------------------------------------
        input_fp = self.fingerprint_agent.ingest_repo(
            input_repo_url,
            input_path,
        )

        # --------------------------------------------------
        # PHASE 1: Fingerprint-only ranking
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

        ranked = [
            r for r in ranked
            if r["repo_url"] != input_repo_url
        ]

        top_candidates = ranked[:top_k]

        logger.info(
            f"[ORCH] TOP-{top_k} candidates: "
            f"{[c['repo_url'] for c in top_candidates]}"
        )

        # --------------------------------------------------
        # PHASE 2: Conditional Agent Execution
        # --------------------------------------------------
        aggregated_results = {}

        for item in top_candidates:
            cand_url = item["repo_url"]
            fp_res = item["fp"]
            cand_path = repo_paths.get(cand_url)

            agent_scores = []

            # -------------------------------
            # Fingerprint (ALWAYS)
            # -------------------------------
            agent_scores.append(fp_res)

            simhash_score = fp_res.get("simhash_score", 0.0)
            winnowing_score = fp_res.get("winnowing_score", 0.0)

            deep_allowed = (
                force_heavy or
                (
                    simhash_score >= simhash_threshold
                    and winnowing_score >= winnowing_threshold
                )
            )

            # -------------------------------
            # Structural Agent
            # -------------------------------
            if cand_path and deep_allowed:
                try:
                    agent_scores.append(
                        self.structural_agent.run(
                            input_path,
                            cand_path,
                            simhash_score=simhash_score,
                        )
                    )
                except Exception:
                    logger.exception(f"[STRUCTURAL ERROR] {cand_url}")
                    agent_scores.append({
                        "agent": "structural",
                        "score": 0.0,
                        "details": {
                            "status": "error",
                            "reason": "structural_exception",
                        },
                    })
            else:
                agent_scores.append({
                    "agent": "structural",
                    "score": 0.0,
                    "details": {
                        "status": "skipped",
                        "reason": "fingerprint_below_threshold",
                        "simhash": simhash_score,
                        "winnowing": winnowing_score,
                    },
                })

            # -------------------------------
            # Semantic Agent
            # -------------------------------
            if cand_path and deep_allowed:
                try:
                    agent_scores.append(
                        self.semantic_agent.run(
                            input_path,
                            cand_path,
                        )
                    )
                except Exception:
                    logger.exception(f"[SEMANTIC ERROR] {cand_url}")
                    agent_scores.append({
                        "agent": "semantic",
                        "score": 0.0,
                        "details": {
                            "status": "error",
                            "reason": "semantic_exception",
                        },
                    })
            else:
                agent_scores.append({
                    "agent": "semantic",
                    "score": 0.0,
                    "details": {
                        "status": "skipped",
                        "reason": "fingerprint_below_threshold",
                    },
                })

            # -------------------------------
            # Contributor Agent (ALWAYS)
            # -------------------------------
            try:
                agent_scores.append(
                    self.contributor_agent.run(
                        input_path,
                        cand_path,
                    )
                )
            except Exception:
                logger.exception(f"[CONTRIBUTOR ERROR] {cand_url}")
                agent_scores.append({
                    "agent": "contributor",
                    "score": 0.0,
                    "details": {
                        "status": "error",
                        "reason": "contributor_exception",
                    },
                })

            aggregated_results[cand_url] = agent_scores

        # --------------------------------------------------
        # FINAL: Aggregate scores
        # --------------------------------------------------
        return aggregate_multiple_repos(aggregated_results)
