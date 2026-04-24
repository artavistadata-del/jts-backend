# config/dept_registry.py

# Import semua model yang tersedia
from models.models.models import FactFinance 
# from models.models.models import FactHR  <-- Contoh untuk nanti

# Import semua fungsi pembersih khusus
from cleaners.finance_cleanser import process_finance_excel
# from cleaners.hr_cleanser import process_hr_excel <-- Contoh untuk nanti

DEPT_CONFIG = {
    1: { # 1 = ID Departemen Finance
        "name": "Finance",
        "model": FactFinance,
        "table_name": "oltp_tes.fact_finance", 
        "cleanser": process_finance_excel,
        "unique_keys": [
                "bulan", 
                "account_name", 
                "report_type", 
                "idx_category", 
                "category", 
                "idx_sub_category", 
                "sub_category", 
                "sub_sub_category"
            ],
        "constraint_name": "uix_finance_data",
        "dept_name": "Finance",
    },
    # CONTOH JIKA BESOK ADA DEPARTEMEN HR (ID 2):
    # 2: {
    #     "name": "Human Resources",
    #     "model": FactHR,
    #     "table_name": "oltp_tes.fact_hr",
    #     "cleanser": process_hr_excel,
    #     "unique_keys": ["bulan", "nik_karyawan", "komponen_gaji"],
    #     "constraint_name": "uix_hr_data"
    # }
}

def get_dept_config(id_dept: int) -> dict:
    if id_dept not in DEPT_CONFIG:
        raise ValueError(f"Sistem belum mendukung integrasi untuk ID Departemen: {id_dept}")
    return DEPT_CONFIG[id_dept]