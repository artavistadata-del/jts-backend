DEPARTMENT_CONFIG = {
    'FINANCE' : {
        'name' : 'finance',
        "powerbi": {
            "report_id": "0ad73404-1eda-4f22-b16e-e494b47205ec",
            "dataset_id": "f2716cdf-218f-4789-bffc-453fe4b3d8db",
        }
    },
    'PURCHASING' : {
        'name' : 'purchasing',
        "powerbi": {
            "report_id": "b5284068-cb63-41c9-ad98-d00aac2019f8",
            "dataset_id": "97c8dd60-c7c0-43ce-8fa5-d7f36a5cc447",
        },
    },
    'SALES' : {
        'name' : 'sales',
        "powerbi": {
            "report_id": "afe0aa04-c1af-4ea3-9160-8c541524a730",
            "dataset_id": "d1f9397f-a047-4321-a33f-3ada3009c600",
        },
    }
}

def get_dept_config(name: str) -> dict:
    if name not in DEPARTMENT_CONFIG:
        # raise ValueError(f"Sistem belum mendukung integrasi untuk ID Departemen: {id_dept}")
        raise ValueError(f"Sistem belum mendukung integrasi untuk Departmnet Ini{name}")
    return DEPARTMENT_CONFIG[name]

def get_powerbi_config(name : str) -> dict:
    """Fungsi pembantu khusus untuk mengambil konfigurasi Power BI."""
    config = get_dept_config(name)
    if "powerbi" not in config:
        raise ValueError(f"Departemen {config['name']} belum memiliki konfigurasi Power BI.")
    return config["powerbi"]