from celery import Celery

celery_app = Celery(
    "dashboard_worker",
    broker="redis://localhost:6379/0",
    include=["cleaning.tasks"] 
)

celery_app.conf.update(
    task_ignore_result=True, 
    task_store_errors_even_if_ignored=True, 
    timezone='Asia/Jakarta',
)