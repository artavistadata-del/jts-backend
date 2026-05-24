from typing import List

from src.modules.history.service import HistoryService
from src.modules.transaction.finance.repository import FinanceTransactionRepository

class FinanceTransactionService:
    def __init__(self, repo: FinanceTransactionRepository, history_service : HistoryService):
        self.repo = repo
        self.history_service = history_service

    

    # ==========================================
    # GET ALL FINANCE TRANSACTIONS
    # ==========================================
    
    def get_finance_transactions(
        self, skip: int, limit: int, report_type: str = None,
        years: List[int] = None, months: List[int] = None, categories: List[str] = None,
        search: str = None, sort_by: str = "year", sort_order: str = "desc"
    ):
        results, has_next = self.repo.get_all_finance_data(
            skip=skip, limit=limit, report_type=report_type,
            years=years, months=months, categories=categories,
            search=search, sort_by=sort_by, sort_order=sort_order
        )

        return {
            "success": True,
            "message": "Data transaksi finance berhasil diambil",
            "data": results,
            "meta": {
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "has_next_page": has_next
                },
                "filters": {
                    "report_type": report_type,
                    "years": years,
                    "months": months,
                    "categories": categories,
                    "search_category": search
                },
                "sorting": {
                    "sort_by": sort_by,
                    "sort_order": sort_order
                }
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
    

    def get_filter_options(self):
        """Service untuk mendapatkan list dropdown filter"""
        options = self.repo.get_finance_filter_options()

        return {
            "success": True,
            "message": "Opsi filter berhasil diambil",
            "data": options
        }