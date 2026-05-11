from fastapi import HTTPException
from sqlalchemy import text
from src.infra.upload.schema import ConfirmUploadInput
from src.workers.cleaning.tasks import commit_upsert_task
from src.modules.departments.registry import get_dept_config
from src.models.models import History as HistoryUploadModels, StatusEnum, Users
from src.modules.history.schema import HistoryUpload as HistoryUploadSchema
from src.modules.history.repository import HistoryRepository 


class HistoryService :
    def __init__(self, history_repo : HistoryRepository):
        self.history_repo = history_repo

    # ==========================================
    # ADD HISTORY
    # ==========================================
    def add_history(self, history_schema : HistoryUploadSchema):

        final_status = history_schema.status if history_schema.status is not None else StatusEnum.ANALYZING

        history_models = HistoryUploadModels(
            user_id = history_schema.user_id,
            role_id = history_schema.role_id,
            department_id = history_schema.department_id,
            file_name = history_schema.file_name,
            # time_stamp = history_schema.time_stamp,
            file_name_storage = history_schema.file_name_storage,
            status=final_status
    
        )
        return self.history_repo.insert_history(history_models)
    
    # ==========================================
    # GEL ALL HISTORY
    # ==========================================
    def get_history_paginated(self, userNow: Users, page: int = 1, size: int = 10):
        if page < 1:
            page = 1
        if size < 1:
            size = 10
        skip = (page - 1) * size
        
        # Ekstrak data yang dibutuhkan dari userNow
        id_user = userNow.id
        role_name = userNow.role.name.value if userNow.role else "STAFF"
        id_dept = userNow.department_id

        # Panggil method repository yang baru
        items, total = self.history_repo.get_history_by_access(
            id_users=id_user, 
            role_name=role_name, 
            id_dept=id_dept, 
            skip=skip, 
            limit=size
        )
        
        return {
            "data": items,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": (total + size - 1) // size 
        }
    
    # ==========================================
    # GET HISTORY BY ID
    # ==========================================
    def get_history_by_id(self, id_hist : int) :
        return self.history_repo.get_history_by_id_hist(id_hist)
    
    # ==========================================
    # GET HISTORY BY UUID
    # ==========================================
    def get_history_by_uuid(self, uuid_hist : str) :
        return self.history_repo.get_history_by_uuid_hist(uuid_hist)
    
    # ==========================================
    # CONFIRM UPLOAD
    # ==========================================
    def confirm_and_process_upload(self, history_id: int, action : str):
        record = self.history_repo.get_history_by_id_hist(history_id)
        
        if not record or record.status != StatusEnum.AWAITING_PREVIEW:
            raise HTTPException(status_code=400, detail="Status data tidak valid untuk konfirmasi.")

        record.status = StatusEnum.PROCESSING_INSERT
        
        self.history_repo.update_history(record)
        
        commit_upsert_task.delay(history_id, record.file_name, record.department_id, action.value)

        return True
    

    # ==========================================
    # PREVIEW HISTORY -> APPROVE/REJECT [ ADMIN ]
    # ==========================================
    def review_history(self, history_id: str, action: StatusEnum, note: str, manager_id_dept: int):

        record = self.history_repo.get_history_by_uuid_hist(history_id)
        
        if not record:
            raise HTTPException(status_code=404, detail="Data History tidak ditemukan.")

        # 2. Keamanan: Cegah Manager mereview data departemen lain
        if record.department_id != manager_id_dept:
            raise HTTPException(status_code=403, detail="Anda tidak berhak me-review file dari departemen lain.")

        # 3. Validasi status harus PENDING
        if record.status != StatusEnum.PENDING:
            raise HTTPException(status_code=400, detail=f"File berstatus {record.status.value}, tidak bisa direview.")

        # 4. Ambil konfigurasi model (FactFinance/HR/dll) dari registry
        config = get_dept_config(record.department_id)
        # target_model = config["model"]

        # 5. EKSEKUSI REJECT ATAU APPROVE
        if action == StatusEnum.REJECTED:
            # Hapus data transaksi
            # self.history_repo.delete_related_facts(target_model, record.id)
            
            # Update status history & catatan
            record.status = StatusEnum.REJECTED
            record.note = note
            self.history_repo.update_history(record)
            
            return "File ditolak. Data transaksi berhasil dihapus dari sistem."

        elif action == StatusEnum.APPROVED:
            # Update status history & catatan
            record.status = StatusEnum.APPROVED
            record.note = note
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
