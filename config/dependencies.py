from fastapi import Depends
from minio import Minio
from sqlalchemy.orm import Session
from config.config import get_db, minio_client_instance
from core.security import get_current_user
from models.models import Users
from repositories.department_repository import DepartmentRepository
from repositories.history_repository import HistoryRepository
from repositories.role_repository import RoleRepository
from repositories.user_repository import UserRepository
from services.history_service import HistoryService
from services.minio_service import MinioService
from services.user_service import UserService

# Bergantung pada get_db
def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_role_repo(db: Session = Depends(get_db)) -> RoleRepository:
    return RoleRepository(db)

def get_dept_repo(db: Session = Depends(get_db)) -> DepartmentRepository:
    return DepartmentRepository(db)

def get_hist_repo(db: Session = Depends(get_db)) -> HistoryRepository:
    return HistoryRepository(db)

def get_user_service(user_repo: UserRepository = Depends(get_user_repo), role_repo : RoleRepository = Depends(get_role_repo), dept_repo : DepartmentRepository = Depends(get_dept_repo)) -> UserService:
    return UserService(user_repo=user_repo, role_repo=role_repo, dept_repo=dept_repo)

def get_minio_client():
    return minio_client_instance

def get_history_service(history_repo : HistoryRepository = Depends(get_hist_repo)):
    return HistoryService(history_repo=history_repo)

def get_minio_service(client : Minio = Depends(get_minio_client), user : Users = Depends(get_current_user), upload_service : HistoryService = Depends(get_history_service)) -> MinioService:
    return MinioService(client, user, upload_service)