from datetime import datetime
import os
import uuid
from fastapi import HTTPException
from src.modules.departments.service import DepartmentService
from src.workers.cleaning.tasks import analyze_excel_task
from src.models.models import RoleEnum, Users
from src.modules.history.schema import HistoryUpload as HistoryUploadSchema
from src.modules.history.service import HistoryService
from src.infra.upload.repository import UploadRepository
from typing import Optional
import typing

class UploadService:
    def __init__(self, minio_repo: UploadRepository, history_service: HistoryService, department_service : DepartmentService):
        self.minio_repo = minio_repo
        self.history_service = history_service
        self.department_service = department_service
    

    # ==========================================
    # UPLOAD FILE [USER ACCESS]
    # ==========================================
    def process_payroll_upload(self, 
            file_name: str,
            file_stream: typing.BinaryIO,
            file_size: int,
            content_type: str,
            user_now : Users,
            target_department_id: Optional[str] = None,
        ):
        """Mengorkestrasi upload MinIO dan pencatatan histori Database"""
        
        final_department_id = None

        if user_now.role.name == RoleEnum.ADMIN.value:
            if not target_department_id:
                raise HTTPException(
                    status_code=400, 
                    detail="Department ID harus disertakan untuk admin."
                )
            
            department_find = self.department_service.display_dept_by_uuid(target_department_id)
            if not department_find:
                raise HTTPException(
                    status_code=404,
                    detail="Department Tidak Ditemukan"
                )
            
            final_department_id = department_find.id 

        else:
            # --- RULES UNTUK STAFF / MANAGER ---
            final_department_id = user_now.department_id
            result = self.department_service.display_dept_by_id(final_department_id)
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="Department Tidak Ditemukan"
                )

        try:
            original_name, ext = os.path.splitext(file_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            random_id = uuid.uuid4().hex[:8]
            storage_name = f"{timestamp}_{random_id}{ext}"
            
            minio_data = self.minio_repo.upload_file(
                file_name=storage_name,
                file_stream=file_stream,
                file_size=file_size,
                content_type=content_type,
                dept_id= user_now.department_id if final_department_id == None else final_department_id
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}

        history_schema = HistoryUploadSchema(
            file_name=file_name,
            user_id=user_now.id,
            department_id=final_department_id,
            time_stamp=datetime.now().date(),
            role_id=user_now.role_id,
            file_name_storage= storage_name
        )
        
        success_upload = self.history_service.add_history(history_schema=history_schema)

        result =  success_upload.public_id, success_upload.id

        analyze_excel_task.delay(result[1], storage_name, final_department_id)

        return {
            "status": "success",
            "message": "File berhasil diunggah dan histori dicatat.",
            "data": {
                "history_id" : result[0],
                "file_name" : file_name
            }
        }