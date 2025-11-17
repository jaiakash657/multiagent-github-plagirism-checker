from pydantic import BaseModel, Field
from typing import List, Optional, Any


# ------------------------------
# Input Request Schema
# ------------------------------
class AnalyzeRequest(BaseModel):
    repo_url: str = Field(..., example="https://github.com/user/repo.git")
    depth: Optional[int] = Field(1, ge=1, le=5)


# ------------------------------
# Agent Score Breakdown
# ------------------------------
class AgentResult(BaseModel):
    agent: str
    score: float
    details: Optional[dict] = None


# ------------------------------
# Per-Repository Aggregated Result
# ------------------------------
class RepoScore(BaseModel):
    repo_url: str
    final_similarity: float
    agent_scores: List[AgentResult]


# ------------------------------
# Top 3 Similar Repo Schema
# ------------------------------
class SimilarRepo(BaseModel):
    repo_url: str
    final_similarity: float
    agent_scores: Optional[List[AgentResult]] = None


# ------------------------------
# Legacy Single-Repo Response
# ------------------------------
class AnalyzeResponse(BaseModel):
    repo_url: str
    results: List[AgentResult]
    aggregated_score: float


# ------------------------------
# Job + Celery Status Responses
# ------------------------------
class JobResponse(BaseModel):
    job_id: str
    status: str


class StatusResponse(BaseModel):
    job_id: str
    status: str
    detail: Optional[Any] = None


# ------------------------------
# Final Multi-Repo Result Response
# ------------------------------
class TaskFinalResult(BaseModel):
    input_repo: str
    top_3_repos: List[SimilarRepo]
    all_repo_scores: List[RepoScore]
    report_path: Optional[str]
    status: str


class ResultResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[TaskFinalResult] = None
