# backend/main.py

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
    description="Backend API for multi-agent GitHub repo similarity analysis"
)

# -------------------------------------------------
# CORS Middleware
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update later for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Include Routers
# -------------------------------------------------
app.include_router(analysis_router, prefix="/api")
app.include_router(status_router, prefix="/api")

# -------------------------------------------------
# Root & Health Endpoints
# -------------------------------------------------
@app.get("/")
def root():
    return {"message": "Backend is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
