from fastapi import Depends
from minio import Minio
from sqlalchemy.orm import Session
from src.core.database import get_db, get_minio_client
from src.modules.departments.service import DepartmentService
from src.models.models import Users
from src.modules.departments.repository import DepartmentRepository
from src.modules.history.repository import HistoryRepository
from src.modules.roles.repository import RoleRepository
from src.modules.roles.service import RoleService
from src.modules.transaction.repository import TransactionRepository
from src.modules.transaction.service import TransactionService
from src.infra.upload.repository import UploadRepository
from src.modules.users.repository import UserRepository
from src.modules.history.service import HistoryService
from src.infra.upload.service import UploadService
from src.modules.users.service import UserService

# Bergantung pada get_db
def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_role_repo(db: Session = Depends(get_db)) -> RoleRepository:
    return RoleRepository(db)

def get_dept_repo(db: Session = Depends(get_db)) -> DepartmentRepository:
    return DepartmentRepository(db)

def get_hist_repo(db: Session = Depends(get_db)) -> HistoryRepository:
    return HistoryRepository(db)

def get_transaction_repo(db: Session = Depends(get_db)) -> TransactionRepository:
    return TransactionRepository(db)

def get_role_service(role_repo : RoleRepository = Depends(get_role_repo)):
    return RoleService(role_repo)

def get_dept_service(dept_repo : DepartmentRepository = Depends(get_dept_repo)):
    return DepartmentService(dept_repo)

def get_user_service(user_repo: UserRepository = Depends(get_user_repo), role_service : RoleService = Depends(get_role_service), dept_service : DepartmentService = Depends(get_dept_service)) -> UserService:
    return UserService(user_repo=user_repo, role_service=role_service, dept_service=dept_service)


def get_history_service(history_repo : HistoryRepository = Depends(get_hist_repo)):
    return HistoryService(history_repo=history_repo)

def get_minio_repo(client : Minio = Depends(get_minio_client)) -> UploadRepository:
    return UploadRepository(client)

def get_minio_service(minio_repo : UploadRepository = Depends(get_minio_repo), history_service : HistoryService = Depends(get_history_service), departments_service : DepartmentService = Depends(get_dept_service)) -> UploadService:
    return UploadService(minio_repo, history_service, departments_service)

def get_transaction_service(transaction_repo : TransactionRepository = Depends(get_transaction_repo), history_service : HistoryService = Depends(get_history_service)) -> TransactionService :
    return TransactionService(transaction_repo, history_service)