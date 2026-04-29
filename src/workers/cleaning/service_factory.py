from src.workers.cleaning.finance_service import FinanceService
# from cleaning.services.hr_service import HRService  # Nanti kalau sudah ada

def get_cleaning_service(id_dept: int, db_session):
    if id_dept == 1:
        return FinanceService(db_session)
    # elif id_dept == 2:
    #     return HRService(db_session)
    else:
        raise ValueError(f"Service untuk Department ID {id_dept} belum tersedia.")