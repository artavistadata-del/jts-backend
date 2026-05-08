from datetime import datetime
import os
import uuid
from src.workers.cleaning.tasks import analyze_excel_task
from src.models.models import Users
from src.modules.history.schema import HistoryUpload as HistoryUploadSchema
from src.modules.history.service import HistoryService
from src.infra.upload.repository import UploadRepository
from typing import Optional
import typing

class UploadService:
    def __init__(self, minio_repo: UploadRepository, history_service: HistoryService):
        self.minio_repo = minio_repo
        self.history_service = history_service
    

    # ==========================================
    # UPLOAD FILE [USER ACCESS]
    # ==========================================
    def process_payroll_upload(self, user: Users, file_name: str, file_stream: typing.BinaryIO, file_size: int, content_type: str, target_dept_id: Optional[int] = None):
        """Mengorkestrasi upload MinIO dan pencatatan histori Database"""
        

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
                dept_id= user.department_id if target_dept_id == None else target_dept_id
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}

        history_schema = HistoryUploadSchema(
            file_name=file_name,
            user_id=user.id,
            department_id=target_dept_id,
            time_stamp=datetime.now().date(),
            role_id=user.role_id,
            file_name_storage= storage_name
        )
        
        success_upload = self.history_service.add_history(history_schema=history_schema)

        result =  success_upload.public_id, success_upload.id

        analyze_excel_task.delay(result[1], storage_name, target_dept_id)

        return {
            "status": "success",
            "message": "File berhasil diunggah dan histori dicatat.",
            "data": {
                "history_id" : result[0],
                "file_name" : file_name
            }
        }