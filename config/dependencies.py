from fastapi import Depends
from minio import Minio
from sqlalchemy.orm import Session
from config.config import get_db, get_minio_client
# from core.security import get_current_user
from departments.department_service import DepartmentService
# from finance.finance_repository import FinanceRepository
# from finance.finance_service import FinanceService
from models.models.models import Users
from departments.department_repository import DepartmentRepository
from history.history_repository import HistoryRepository
from roles.role_repository import RoleRepository
from roles.role_service import RoleService
from transaction.transaction_repository import TransactionRepository
from transaction.transaction_service import TransactionService
from upload.minio_repository import MinioRepository
from users.user_repository import UserRepository
from history.history_service import HistoryService
from upload.minio_service import MinioService
from users.user_service import UserService

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


# def get_finance_repo(db: Session = Depends(get_db)) -> FinanceRepository:
#     return FinanceRepository(db)

def get_role_service(role_repo : RoleRepository = Depends(get_role_repo)):
    return RoleService(role_repo)

def get_dept_service(dept_repo : DepartmentRepository = Depends(get_dept_repo)):
    return DepartmentService(dept_repo)

def get_user_service(user_repo: UserRepository = Depends(get_user_repo), role_service : RoleService = Depends(get_role_service), dept_service : DepartmentService = Depends(get_dept_service)) -> UserService:
    return UserService(user_repo=user_repo, role_service=role_service, dept_service=dept_service)


def get_history_service(history_repo : HistoryRepository = Depends(get_hist_repo)):
    return HistoryService(history_repo=history_repo)


def get_minio_repo(client : Minio = Depends(get_minio_client)) -> MinioRepository:
    return MinioRepository(client)

# def get_minio_service(client : Minio = Depends(get_minio_client), user : Users = Depends(get_current_user), upload_service : HistoryService = Depends(get_history_service)) -> MinioService:
#     return MinioService(client, user, upload_service)

def get_minio_service(minio_repo : MinioRepository = Depends(get_minio_repo), history_service : HistoryService = Depends(get_history_service)) -> MinioService:
    return MinioService(minio_repo, history_service)

# def get_finance_service(finance_repo : FinanceRepository = Depends(get_finance_repo)) -> FinanceService:
#     return FinanceService(finance_repo)

def get_transaction_service(transaction_repo : TransactionRepository = Depends(get_transaction_repo)) -> TransactionService :
    return TransactionService(transaction_repo)