from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from workers.celery_app import celery_app
from api.schemas import StatusResponse, ResultResponse

router = APIRouter()

@router.get("/status/{job_id}", response_model=StatusResponse)
async def task_status(job_id: str):
    """
    Return Celery task status:
    - PENDING
    - STARTED
    - SUCCESS
    - FAILURE
    - RETRY
    """
    try:
        result = AsyncResult(job_id, app=celery_app)
        detail = None

        # If failed, include minimal error info
        if result.status == "FAILURE":
            detail = str(result.result)

        return StatusResponse(
            job_id=job_id,
            status=result.status,
            detail=detail
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{job_id}", response_model=ResultResponse)
async def task_result(job_id: str):
    """
    Return the final result IF the Celery task has completed.
    If not completed, return status 202 with current state.
    """
    try:
        result = AsyncResult(job_id, app=celery_app)

        # Not ready -> tell client to wait
        if not result.ready():
            raise HTTPException(
                status_code=202,
                detail={"status": result.status}
            )

        # Task finished: return result
        return ResultResponse(
            job_id=job_id,
            status=result.status,
            result=result.result
        )

    except HTTPException:
        # Allow the 202 status to propagate
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
