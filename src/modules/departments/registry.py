from src.models.models import FactFinance 
# from models.models.models import FactHR  <-- Contoh untuk nanti

# Import semua fungsi pembersih khusus
from src.workers.cleanser.finance import process_finance_excel
from src.workers.cleanser.purchasing import process_purchasing_excel
# from cleaners.hr_cleanser import process_hr_excel <-- Contoh untuk nanti

DEPT_CONFIG = {
    1: { # 1 = ID Departemen Finance
        "name": "finance",
        "model": FactFinance,
        "table_name": "oltp_main.fact_finance", 
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
        "mv_refresh_query" : "REFRESH MATERIALIZED VIEW CONCURRENTLY olap_finance.mv_finance_detail;",
        "powerbi": {
            "report_id": "0ad73404-1eda-4f22-b16e-e494b47205ec",
            "dataset_id": "f2716cdf-218f-4789-bffc-453fe4b3d8db",
        }
    },


    2: { # 2 = ID Departemen Purchasing
        "name": "finance",
        "model": FactFinance,
        "table_name": "oltp_main.fact_finance", 
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
        "mv_refresh_query" : "REFRESH MATERIALIZED VIEW CONCURRENTLY olap_finance.mv_finance_detail;",
        "powerbi": {
            "report_id": "b5284068-cb63-41c9-ad98-d00aac2019f8",
            "dataset_id": "97c8dd60-c7c0-43ce-8fa5-d7f36a5cc447",
        }
    },

     3: {
        "name": "purchasing",
        "table_name": None,
        "cleanser": process_purchasing_excel,
        "unique_keys": [],
        "constraint_name": None,
        "dept_name": "Purchasing",
        "mv_refresh_query": None,
        "powerbi": {
            "report_id": "b5284068-cb63-41c9-ad98-d00aac2019f8",
            "dataset_id": "97c8dd60-c7c0-43ce-8fa5-d7f36a5cc447",
        },
    }




    # CONTOH JIKA BESOK ADA DEPARTEMEN HR (ID 2):
    # 2: {
    #     "name": "Human Resources",
    #     "model": FactHR,
    #     "table_name": "oltp_main.fact_hr",
    #     "cleanser": process_hr_excel,
    #     "unique_keys": ["bulan", "nik_karyawan", "komponen_gaji"],
    #     "constraint_name": "uix_hr_data"
    # }
}

def get_dept_config(id_dept: int) -> dict:
    if id_dept not in DEPT_CONFIG:
        # raise ValueError(f"Sistem belum mendukung integrasi untuk ID Departemen: {id_dept}")
        raise ValueError(f"Sistem belum mendukung integrasi untuk Departmnet Ini")
    return DEPT_CONFIG[id_dept]

def get_powerbi_config(id_dept: int) -> dict:
    """Fungsi pembantu khusus untuk mengambil konfigurasi Power BI."""
    config = get_dept_config(id_dept)
    if "powerbi" not in config:
        raise ValueError(f"Departemen {config['name']} belum memiliki konfigurasi Power BI.")
    return config["powerbi"]