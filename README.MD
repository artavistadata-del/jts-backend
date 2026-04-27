celery :

1. cd ~/jts-project/project-dashboard
2. celery -A config.celery_conf worker --loglevel=info

fastAPI :

1. cd ~/jts-project/project-dashboard
2. uvicorn main:app --reload
