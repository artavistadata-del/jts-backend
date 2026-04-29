from datetime import datetime, date
import os
import uuid
from src.workers.cleaning.tasks import analyze_excel_task
from src.models.models.models import Users
from src.modules.history.schema import HistoryUpload as HistoryUploadSchema
from src.modules.history.service import HistoryService
from src.infra.upload.repository import UploadRepository
import typing

class UploadService:
    def __init__(self, minio_repo: UploadRepository, history_service: HistoryService):
        self.minio_repo = minio_repo
        self.history_service = history_service

    def process_payroll_upload(self, user: Users, file_name: str, file_stream: typing.BinaryIO, file_size: int, content_type: str):
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
                dept_id=user.id_dept
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}

        history_schema = HistoryUploadSchema(
            file_name=file_name,
            id_users=user.idusers,
            id_dept=user.id_dept,
            time_stamp=datetime.now().date(),
            id_role=user.id_roles,
            file_name_storage= storage_name
        )
        
        success_upload = self.history_service.add_history(history_schema=history_schema)

        result =  success_upload.id_history_upload

        analyze_excel_task.delay(result, storage_name, user.id_dept)

        return {
            "status": "success",
            "message": "File berhasil diunggah dan histori dicatat.",
            "data": {
                "id_history" : result,
                "file_name" : file_name
            }
        }