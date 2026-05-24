from fastapi import Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.dependencies import get_history_service
from src.modules.history.service import HistoryService
from src.modules.transaction.purchasing.repository import PurchasingTransactionRepository
from src.modules.transaction.purchasing.service import PurchasingTransactionService


def get_purchasing_transaction_repository(db: Session = Depends(get_db)) -> PurchasingTransactionRepository:
    return PurchasingTransactionRepository(db)


def get_purchasing_transaction_service(
        repository : PurchasingTransactionRepository = Depends(get_purchasing_transaction_repository), 
        history_service : HistoryService = Depends(get_history_service)
    ) -> PurchasingTransactionService :

    return PurchasingTransactionService(repo=repository, history_service=history_service)