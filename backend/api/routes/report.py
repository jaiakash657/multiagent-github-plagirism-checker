from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()

REPORTS_DIR = Path("reports")

@router.get("/download/pdf/{report_name}")
def download_pdf(report_name: str):
    pdf_path = REPORTS_DIR / f"{report_name}.pdf"

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=pdf_path.name
    )
