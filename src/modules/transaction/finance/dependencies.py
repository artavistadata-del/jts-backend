from fastapi import Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.dependencies import get_history_service
from src.modules.history.service import HistoryService
from src.modules.transaction.finance.repository import FinanceTransactionRepository
from src.modules.transaction.finance.service import FinanceTransactionService


def get_finance_transaction_repository(db: Session = Depends(get_db)) -> FinanceTransactionRepository:
    return FinanceTransactionRepository(db)


def get_finance_transaction_service(
        repository : FinanceTransactionRepository = Depends(get_finance_transaction_repository), 
        history_service : HistoryService = Depends(get_history_service)
    ) -> FinanceTransactionService :

    return FinanceTransactionService(repo=repository, history_service=history_service)