from fastapi import HTTPException
from sqlalchemy import text
from cleaning.tasks import commit_upsert_task
from config.dept_registry import get_dept_config
from models.models.models import HistoryUpload as HistoryUploadModels, StatusEnum, Users
from models.schemas.history_schema import HistoryUpload as HistoryUploadSchema
from history.history_repository import HistoryRepository 


class HistoryService :
    def __init__(self, history_repo : HistoryRepository):
        self.history_repo = history_repo

    def add_history(self, history_schema : HistoryUploadSchema):
        history_models = HistoryUploadModels(
            id_users = history_schema.id_users,
            id_roles = history_schema.id_role,
            id_dept = history_schema.id_dept,
            file_name = history_schema.file_name,
            time_stamp = history_schema.time_stamp
    
        )
        return self.history_repo.insert_history(history_models)
    

    def get_history_paginated(self, userNow: Users, page: int = 1, size: int = 10):
        if page < 1:
            page = 1
        if size < 1:
            size = 10
        skip = (page - 1) * size
        
        # Ekstrak data yang dibutuhkan dari userNow
        id_user = userNow.idusers
        role_name = userNow.roles.role.value if userNow.roles else "STAFF"
        id_dept = userNow.id_dept

        # Panggil method repository yang baru
        items, total = self.history_repo.get_history_by_access(
            id_users=id_user, 
            role_name=role_name, 
            id_dept=id_dept, 
            skip=skip, 
            limit=size
        )
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": (total + size - 1) // size 
        }
    
    
    def get_history_by_id(self, id_hist : int) :
        return self.history_repo.get_history_by_id_hist(id_hist)
    

    def confirm_and_process_upload(self, history_id: int):
        record = self.history_repo.get_history_by_id_hist(history_id)
        
        if not record or record.status != StatusEnum.AWAITING_PREVIEW:
            raise HTTPException(status_code=400, detail="Status data tidak valid untuk konfirmasi.")

        record.status = StatusEnum.PROCESSING_INSERT
        
        self.history_repo.update_history(record)

        commit_upsert_task.delay(history_id, record.file_name, record.id_dept)

        return True
    


    def review_history(self, history_id: int, action: StatusEnum, notes: str, manager_id_dept: int):

        record = self.history_repo.get_history_by_id_hist(history_id)
        
        if not record:
            raise HTTPException(status_code=404, detail="Data History tidak ditemukan.")

        # 2. Keamanan: Cegah Manager mereview data departemen lain
        if record.id_dept != manager_id_dept:
            raise HTTPException(status_code=403, detail="Anda tidak berhak me-review file dari departemen lain.")

        # 3. Validasi status harus PENDING
        if record.status != StatusEnum.PENDING:
            raise HTTPException(status_code=400, detail=f"File berstatus {record.status.value}, tidak bisa direview.")

        # 4. Ambil konfigurasi model (FactFinance/HR/dll) dari registry
        config = get_dept_config(record.id_dept)
        target_model = config["model"]

        # 5. EKSEKUSI REJECT ATAU APPROVE
        if action == StatusEnum.REJECTED:
            # Hapus data transaksi
            self.history_repo.delete_related_facts(target_model, history_id)
            
            # Update status history & catatan
            record.status = StatusEnum.REJECTED
            # record.notes = notes
            self.history_repo.update_history(record)
            
            return "File ditolak. Data transaksi berhasil dihapus dari sistem."

        elif action == StatusEnum.APPROVED:
            # Update status history & catatan
            record.status = StatusEnum.APPROVED
            # record.notes = notes
            self.history_repo.update_history(record)

            # Eksekusi Refresh Materialized View Power BI
            mv_query = config.get("mv_refresh_query")
            if mv_query:
                try:
                    self.history_repo.db.execute(text(mv_query))
                    self.history_repo.db.commit()
                except Exception as e:
                    self.history_repo.db.rollback()
                    print(f"Peringatan: Gagal refresh Materialized View - {e}")
            
            return "File disetujui. Laporan Power BI telah diperbarui."
            
        else:
            raise HTTPException(status_code=400, detail="Aksi tidak valid. Hanya APPROVED atau REJECTED.")
