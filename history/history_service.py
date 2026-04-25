from fastapi import HTTPException

from cleaning.tasks import commit_upsert_task
from models.models.models import HistoryUpload as HistoryUploadModels, StatusEnum
from models.schemas.history_schema import HistoryUpload as HistoryUploadSchema
from history.history_repository import HistoryRepository 


class HistoryService :
    def __init__(self, history_repo : HistoryRepository):
        self.history_repo = history_repo

    def add_history(self, history_schema : HistoryUploadSchema):
        history_models = HistoryUploadModels(
            users_nik = history_schema.users_nik,
            id_roles = history_schema.id_role,
            id_dept = history_schema.id_dept,
            file_name = history_schema.file_name,
            time_stamp = history_schema.time_stamp
    
        )
        return self.history_repo.insert_history(history_models)
    

    def get_history_paginated(self, nik: str, page: int = 1, size: int = 10):

        if page < 1:
            page = 1
        if size < 1:
            size = 10
        skip = (page - 1) * size
        
        items, total = self.history_repo.select_history_by_nik(nik, skip=skip, limit=size)
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": (total + size - 1) // size  # Pembulatan ke atas
        }
    
    def get_history_by_id(self, id_hist : int) :
        return self.history_repo.select_history_by_id_hist(id_hist)
    

    def confirm_and_process_upload(self, history_id: int):
        record = self.history_repo.select_history_by_id_hist(history_id)
        
        if not record or record.status != StatusEnum.AWAITING_PREVIEW:
            raise HTTPException(status_code=400, detail="Status data tidak valid untuk konfirmasi.")

        record.status = StatusEnum.PROCESSING_INSERT
        
        self.history_repo.update_history(record)

        commit_upsert_task.delay(history_id, record.file_name, record.id_dept)

        return True
