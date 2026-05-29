#!/bin/bash
cd /home/artavista/JTS-PROD/jts-backend
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload