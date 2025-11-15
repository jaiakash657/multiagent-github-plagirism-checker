from pydantic import BaseModel, Field
from typing import List, Optional, Any


class AnalyzeRequest(BaseModel):
    repo_url: str = Field(..., example="https://github.com/user/repo.git")
    depth: Optional[int] = Field(1, ge=1, le=5)


class AgentResult(BaseModel):
    agent: str
    score: float
    details: Optional[dict] = None


class AnalyzeResponse(BaseModel):
    repo_url: str
    results: List[AgentResult]
    aggregated_score: float


class JobResponse(BaseModel):
    job_id: str
    status: str


class StatusResponse(BaseModel):
    job_id: str
    status: str
    detail: Optional[Any] = None


class ResultResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[Any] = None
