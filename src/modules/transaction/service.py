from src.models.models import PurchasingSheet1, PurchasingSheet2, PurchasingSheet3, RoleEnum
from src.modules.history.service import HistoryService
from src.modules.transaction.repository import TransactionRepository
from src.modules.departments.registry import get_dept_config

class TransactionService:
    def __init__(self, repo: TransactionRepository, history_service : HistoryService):
        self.repo = repo
        self.history_service = history_service

    # ==========================================
    # UPDATE TRANSACTION [MANAGER ACCESS ]
    # ==========================================
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
    # ==========================================
    # GET ALL TRANSACTION [MANAGER ACCESS ]
    # ==========================================
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
    

    def get_purchasing_transactions(self, sheet_number: int, skip: int, limit: int):
        
        sheet_map = {
            1: PurchasingSheet1,
            2: PurchasingSheet2,
            3: PurchasingSheet3
        }
        model = sheet_map.get(sheet_number)
        if not model:
            raise ValueError("Nomor sheet harus 1, 2, atau 3.")

        results, has_next = self.repo.get_all_purchasing_data(model, skip, limit)

        return {
            "data": results,
            "pagination": {
                "skip": skip,
                "limit": limit,
                "has_next_page": has_next
            },
            "metadata": {
                "sheet": sheet_number
            }
        }


    # ==========================================
    # GET ALL FINANCE TRANSACTIONS
    # ==========================================
    def get_finance_transactions(self, skip: int, limit: int, report_type: str = None):
        """
        Service khusus untuk menarik data Finance dengan optimasi kolom (tanpa SELECT *)
        serta filter opsional berdasarkan IS / BS.
        """
        results, has_next = self.repo.get_all_finance_data(
            skip=skip, 
            limit=limit, 
            report_type=report_type
        )

        return {
            "data": results,
            "pagination": {
                "skip": skip,
                "limit": limit,
                "has_next_page": has_next
            },
            "metadata": {
                "report_type": report_type
            }
        }
    


    def update_transaction_amount(self, transaction_id: int, amount: float):
        """Service untuk meng-update nilai amount pada finance transactions"""
        updated_data = self.repo.update_finance_transaction(transaction_id, amount)
        
        if not updated_data:
            raise ValueError(f"Data transaksi dengan ID {transaction_id} tidak ditemukan.")
            
        return {
            "status": "success",
            "message": f"Data ID {transaction_id} berhasil di-update.",
            "data": {
                "id": updated_data.id,
                "new_amount": float(updated_data.amount)
            }
        }

    def delete_transaction_record(self, transaction_id: int):
        """Service untuk menghapus data finance transactions"""
        is_deleted = self.repo.delete_finance_transaction(transaction_id)
        
        if not is_deleted:
            raise ValueError(f"Data transaksi dengan ID {transaction_id} tidak ditemukan.")
            
        return {
            "status": "success",
            "message": f"Data ID {transaction_id} berhasil dihapus permanen."
        }
    

    def get_staging_finance_transactions(self, history_id: str, skip: int, limit: int, report_type: str = None):
        """
        Service untuk menarik data Staging Finance berdasarkan history_id
        yang statusnya INSERT atau REPLACE.
        """

        find_history = self.history_service.get_history_by_uuid(history_id)
        results, has_next = self.repo.get_staging_finance_data(
            history_id=find_history.id, # Teruskan ke Repo
            skip=skip, 
            limit=limit, 
            report_type=report_type
        )

        return {
            "status" : True,
            "message" :'Data Preview Berhasil di ambil !',
            "data": results,
            "pagination": {
                "skip": skip,
                "limit": limit,
                "has_next_page": has_next
            },
            "metadata": {
                # "history_id": history_id,
                "report_type": report_type
            }
        }


    def wipe_all_transactions(self):
        """Service berbahaya untuk mengosongkan tabel transaksi"""
        deleted_count = self.repo.wipe_all_finance_transactions()
        
        return {
            "success": True,
            "message": f"DANGER ZONE: Seluruh isi tabel telah dikosongkan. Total {deleted_count} baris dihapus.",
            "data": {
                "deleted_count": deleted_count
            }
        }