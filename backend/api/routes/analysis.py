from fastapi import APIRouter, HTTPException, Body
from celery.result import AsyncResult
from workers.celery_app import celery_app
from api.schemas import StatusResponse, ResultResponse
from workers.tasks import analyze_repository_task

router = APIRouter()


@router.post("/analyze")
async def analyze_repo(repo_url: str = Body(..., embed=True)):
    """
    Step 1: Trigger Celery async job for deep analysis.
    """
    try:
        task = analyze_repository_task.delay(repo_url)
        return {"job_id": task.id, "status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=StatusResponse)
async def task_status(job_id: str):
    """
    Step 2: Check intermediate Celery status.
    """
    try:
        result = AsyncResult(job_id, app=celery_app)
        info = None
        if result.status == "FAILURE":
            info = str(result.result)

        return StatusResponse(
            job_id=job_id,
            status=result.status,
            detail=info
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{job_id}", response_model=ResultResponse)
async def task_result(job_id: str):
    """
    Step 3: Fetch final Celery result (includes top 3 repos now).
    """
    try:
        result = AsyncResult(job_id, app=celery_app)

        if not result.ready():
            # Task STILL running...
            raise HTTPException(status_code=202, detail={"status": result.status})

        # Task finished — returning whatever orchestrator produced
        return ResultResponse(
            job_id=job_id,
            status=result.status,
            result=result.result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
