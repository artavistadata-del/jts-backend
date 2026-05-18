from src.workers.cleaning.fin_service import FinService
from src.workers.cleaning.finance_service import FinanceService
from src.workers.cleaning.pur_service import PurchaseService
from src.workers.cleaning.sales_service import SalesService
from src.workers.cleaning.purchasing_service import PurchasingService
# from cleaning.services.hr_service import HRService  # Nanti kalau sudah ada

def get_cleaning_service(id_dept: int, db_session):
    if id_dept == 1:
        # return FinanceService(db_session)
        return FinService(db_session)
    elif id_dept == 3:
        return PurchaseService(db_session)
    
    elif id_dept == 2:
        return SalesService(db_session)
    # elif id_dept == 3:
    #     return PurchasingService(db_session)
    else:
        raise ValueError(f"Cleaning untuk Department ini belum tersedia.")