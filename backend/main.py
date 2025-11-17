from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from config.logger import logger

# Routers
from api.routes.analysis import router as analysis_router
from api.routes.status import router as status_router


# -------------------------------------------------
# Create FastAPI Application
# -------------------------------------------------
app = FastAPI(
    title="Multi-Agent Repo Analyzer Backend",
    version="1.0.0",
    description="Backend API for GitHub repository similarity analysis using multi-agent architecture"
)


# -------------------------------------------------
# CORS Middleware
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],              # change to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------
# Include API Routers
# -------------------------------------------------
app.include_router(analysis_router, prefix="/api")
app.include_router(status_router, prefix="/api")


# -------------------------------------------------
# Basic Health Checks
# -------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "Backend is running",
        "app": settings.APP_NAME,
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


# -------------------------------------------------
# Run Command (for debugging only)
# uvicorn backend.main:app --reload
# -------------------------------------------------
