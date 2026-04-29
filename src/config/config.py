import os
from celery import Celery
from dotenv import load_dotenv
from minio import Minio
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config.celery_conf import celery_app
from src.config.minio_conf import minio_client

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
MINIO_URL = os.getenv("MINIO_URL")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")


engine = create_engine(DATABASE_URL)
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