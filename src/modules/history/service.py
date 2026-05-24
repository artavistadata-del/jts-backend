from fastapi import HTTPException
from sqlalchemy import text
from src.infra.upload.schema import ConfirmUploadInput
from src.modules.departments.service import DepartmentService
from src.workers.cleaning.tasks import commit_upsert_task
from src.models.models import History as HistoryUploadModels, StatusEnum, Users
from src.modules.history.schema import HistoryUpload as HistoryUploadSchema
from src.modules.history.repository import HistoryRepository 


class HistoryService :
    def __init__(self, history_repo : HistoryRepository, department_service : DepartmentService):
        self.history_repo = history_repo
        self.department_service = department_service

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
    def confirm_and_process_upload(self, history_id: int, action):
        record = self.history_repo.get_history_by_id_hist(history_id)

        if not record or record.status != StatusEnum.AWAITING_PREVIEW:
            raise HTTPException(status_code=400, detail="Status data tidak valid untuk konfirmasi.")

        department = self.department_service.display_dept_by_id(record.department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department tidak ditemukan.")
        
        actual_department_name = department.name

        record.status = StatusEnum.PROCESSING_INSERT
        self.history_repo.update_history(record)
        
        action_str = action.value if hasattr(action, 'value') else str(action)

        commit_upsert_task.delay(
            int(history_id), 
            str(record.file_name), 
            str(actual_department_name).upper(), 
            action_str
        )

        return True
