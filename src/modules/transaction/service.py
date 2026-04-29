from src.models.models.models import RoleEnum
from src.modules.transaction.repository import TransactionRepository
from src.config.dept_registry import get_dept_config

class TransactionService:
    def __init__(self, repo: TransactionRepository):
        self.repo = repo

    def edit_transaction(self, id_dept: int, id_fact: int, new_value: float, manager_nik: str):
        # 1. Tanya registry: "Untuk ID Dept ini, model tabelnya apa?"
        config = get_dept_config(id_dept)
        target_model = config["model"] # Mengembalikan class FactFinance
        
        # 2. Lempar model tersebut ke Repository
        return self.repo.update_single_row(
            model_class=target_model,
            id_fact=id_fact,
            new_value=new_value,
            manager_nik=manager_nik
        )
    
    def list_transactions(self, id_dept: int, page: int, size: int, user_role: str, user_id: int, report_type: str = None):
        # 1. Ambil model dinamis sesuai departemen
        config = get_dept_config(id_dept)
        target_model = config["model"]
        
        skip = (page - 1) * size
        
        # 2. Penentuan Filter: Jika Manager, nik_filter = None
        user_id_filter = None if user_role == RoleEnum.MANAGER else user_id

        # 3. Eksekusi query dengan mengirim report_type
        items, total = self.repo.get_paginated_transactions(
            model_class=target_model, 
            skip=skip, 
            limit=size,
            user_id_filter=user_id_filter,
            report_type=report_type # Tambahan
        )
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": (total + size - 1) // size
        }