from datetime import datetime, date
from cleaning.tasks import analyze_excel_task
from models.models.models import Users
from models.schemas.history_schema import HistoryUpload as HistoryUploadSchema
from history.history_service import HistoryService
from upload.minio_repository import MinioRepository
import typing

class MinioService:
    def __init__(self, minio_repo: MinioRepository, history_service: HistoryService):
        self.minio_repo = minio_repo
        self.history_service = history_service

    def process_payroll_upload(self, user: Users, file_name: str, file_stream: typing.BinaryIO, file_size: int, content_type: str):
        """Mengorkestrasi upload MinIO dan pencatatan histori Database"""
        
        try:
            minio_data = self.minio_repo.upload_file(
                file_name=file_name,
                file_stream=file_stream,
                file_size=file_size,
                content_type=content_type
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}

        history_schema = HistoryUploadSchema(
            file_name=file_name,
            id_users=user.idusers,
            id_dept=user.id_dept,
            time_stamp=datetime.now().date(),
            id_role=user.id_roles
        )
        
        success_upload = self.history_service.add_history(history_schema=history_schema)

        result =  success_upload.id_history_upload, file_name

        analyze_excel_task.delay(result[0], result[1], user.id_dept)

        return {
            "status": "success",
            "message": "File berhasil diunggah dan histori dicatat.",
            "data": result
        }