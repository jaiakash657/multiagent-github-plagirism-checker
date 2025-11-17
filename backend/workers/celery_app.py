import os
import sys

# backend/workers → backend/
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from celery import Celery
from config.settings import settings

celery_app = Celery(
    "multiagent_repo_analyzer",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Autodiscover tasks inside workers/
celery_app.autodiscover_tasks(["workers"])

# Optional configs
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    worker_concurrency=4,
    task_track_started=True,
)
