from workers.celery_app import celery
from core.utils import clone_repo, cleanup
from core.orchestrator import orchestrate_analysis
from MultiAgent.backend.core.aggregator import aggregate_agent_scores
from storage.db import init_db, SessionLocal, AnalysisResult
import os
import tempfile

@celery.task(bind=True)
def analyze_repository_task(self, repo_url: str, depth: int = 1):
    """
    Celery task to clone a repo, run agents, aggregate results, store in DB.
    Returns a serializable dict for quick responses.
    """
    path = None
    try:
        path = clone_repo(repo_url)
        agent_results = orchestrate_analysis(path, depth=depth)
        aggregated = aggregate_agent_scores(agent_results)
        # store in DB (best-effort)
        try:
            init_db()
            db = SessionLocal()
            ar = AnalysisResult(repo_url=repo_url, aggregated_score=aggregated["aggregated_score"], details=aggregated)
            db.add(ar)
            db.commit()
            db.close()
        except Exception:
            pass
        return {"repo_url": repo_url, "results": agent_results, "aggregated_score": aggregated["aggregated_score"]}
    finally:
        if path:
            cleanup(path)
