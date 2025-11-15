from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from workers.celery_app import celery_app
from api.schemas import StatusResponse, ResultResponse

router = APIRouter()

@router.get("/status/{job_id}", response_model=StatusResponse)
async def task_status(job_id: str):
    """Return Celery task status such as PENDING, STARTED, SUCCESS, FAILURE."""
    try:
        result = AsyncResult(job_id, app=celery_app)
        info = None
        if result.status == "FAILURE":
            info = str(result.result)
        return StatusResponse(job_id=job_id, status=result.status, detail=info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{job_id}", response_model=ResultResponse)
async def task_result(job_id: str):
    """Return result of Celery task if available; otherwise return 202 with status."""
    try:
        result = AsyncResult(job_id, app=celery_app)

        if not result.ready():
            raise HTTPException(status_code=202, detail={"status": result.status})

        return ResultResponse(job_id=job_id, status=result.status, result=result.result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
