from src.modules.history.service import HistoryService
from src.modules.transaction.purchasing.repository import PurchasingTransactionRepository

class PurchasingTransactionService:
    def __init__(self, repo: PurchasingTransactionRepository, history_service: HistoryService):
        self.repo = repo
        self.history_service = history_service

    def get_purchasing_transactions(
        self, 
        sheet_type: str, 
        skip: int, 
        limit: int
    ):
        # Validasi nama sheet agar aman
        valid_sheets = ["sheet1", "sheet2", "sheet3"]
        if sheet_type not in valid_sheets:
            raise ValueError(f"sheet_type tidak valid. Gunakan salah satu dari: {', '.join(valid_sheets)}")

        results, has_next = self.repo.get_all_purchasing_data(
            sheet_type=sheet_type, 
            skip=skip, 
            limit=limit
        )

        return {
            "success": True,
            "message": f"Data transaksi purchasing {sheet_type} berhasil diambil",
            "data": results,
            "meta": {
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "has_next_page": has_next
                },
                "filters": {
                    "sheet_type": sheet_type
                }
            }
        }
    

    # ==========================================
    # GET STAGING PREVIEW
    # ==========================================
    def get_staging_transactions(self, sheet_type: str, history_id_public: str, skip: int, limit: int):
        valid_sheets = ["sheet1", "sheet2", "sheet3"]
        if sheet_type not in valid_sheets:
            raise ValueError("sheet_type tidak valid. Gunakan 'sheet1', 'sheet2', atau 'sheet3'.")

        # Resolve public_id ke internal ID
        history = self.history_service.get_history_by_uuid(history_id_public)
        if not history:
            raise ValueError(f"History dengan ID {history_id_public} tidak ditemukan.")

        results, has_next = self.repo.get_staging_purchasing_data(
            sheet_type=sheet_type, 
            history_id=history.id, 
            skip=skip, 
            limit=limit
        )

        return {
            "success": True,
            "message": f"Preview Staging {sheet_type} (Insert & Replace) berhasil diambil",
            "data": results,
            "meta": {
                "pagination": {
                    "skip": skip, 
                    "limit": limit, 
                    "has_next_page": has_next
                },
                "filters": {
                    "sheet_type": sheet_type
                }
            }
        }