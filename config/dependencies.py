from fastapi import Depends
from minio import Minio
from sqlalchemy.orm import Session
from config.config import get_db, minio_client_instance
from repositories.user_repository import UserRepository
from services.minio_service import MinioService
from services.user_service import UserService

# Bergantung pada get_db
def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_user_service(repo: UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(repo)

def get_minio_client():
    return minio_client_instance

def get_minio_service(client : Minio = Depends(get_minio_client)) -> MinioService:
    return MinioService(client)