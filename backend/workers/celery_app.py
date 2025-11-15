from celery import Celery
from config.settings import settings

celery = Celery(
    "multiagent",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Basic config
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    timezone="UTC",
)
