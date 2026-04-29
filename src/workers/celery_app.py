from celery import Celery
from src.core.config import settings

celery_app = Celery(
    "dashboard_worker",
    broker=settings.REDIS_URL_CELERY,
    include=["src.workers.cleaning.tasks"] 
)

celery_app.conf.update(
    task_ignore_result=True, 
    task_store_errors_even_if_ignored=True, 
    timezone='Asia/Jakarta',
)