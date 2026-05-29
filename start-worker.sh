#!/bin/bash
cd /home/artavista/JTS-PROD/jts-backend
source venv/bin/activate
celery -A src.workers.celery_app worker --loglevel=info