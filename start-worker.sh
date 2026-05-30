#!/bin/bash
cd /home/artavista/JTS-PROD/jts-backend
source venv/bin/activate

sleep 15

celery -A src.workers.celery_app worker --loglevel=info