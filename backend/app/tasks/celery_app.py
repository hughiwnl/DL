from celery import Celery

from app.config import settings

celery_app = Celery(
    "dl_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.download_task"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    worker_concurrency=settings.MAX_CONCURRENT_DOWNLOADS,
    task_acks_late=True,
)
