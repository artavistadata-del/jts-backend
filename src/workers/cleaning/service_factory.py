from src.workers.cleaning.finance_service import FinanceService
from src.workers.cleaning.purchasing_service import PurchasingService
from src.workers.cleaning.sales_service import SalesService


# def get_cleaning_service(id_dept: int, db_session):
#     if id_dept == 1:
#         return FinanceService(db_session)
#     elif id_dept == 3:
#         return PurchasingService(db_session)
#     elif id_dept == 2:
#         return SalesService(db_session)
#     else:
#         raise ValueError(f"Cleaning untuk Department ini belum tersedia.")

def get_cleaning_service(name : str, db_session):
    if name == "FINANCE":
        return FinanceService(db_session)
    elif name == "PURCHASING":
        return PurchasingService(db_session)
    elif name == "SALES":
        return SalesService(db_session)
    else:
        raise ValueError(f"Cleaning untuk Department ini belum tersedia.{name}")
