from celery import Celery
from minio import Minio
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.workers.celery_app import celery_app
from src.infra.upload.client import minio_client
from src.core.config import settings


engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()




def get_db():
    db = SessionLocal()
    try :
        yield db
    finally :
        db.close()

def get_minio_client() -> Minio :
    return minio_client

def get_celery_client() -> Celery :
    return celery_app