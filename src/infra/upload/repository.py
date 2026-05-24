from minio import Minio, S3Error
import typing
from src.modules.departments.registry import get_dept_config

class UploadRepository:
    def __init__(self, client: Minio):
        self.client = client

    # ==========================================
    # UPLOAD FILE [MANAGER & USER ACCESS]
    # ==========================================
    def upload_file(self, file_name: str, file_stream: typing.BinaryIO, file_size: int, content_type: str, department_name : str):
        """Hanya bertugas mengirim file fisik ke MinIO"""

        bucket_name = get_dept_config(department_name)
        bucket_name = bucket_name['name']
        try:
            file_stream.seek(0) 
            
            result = self.client.put_object(
                bucket_name=bucket_name,
                object_name=file_name,
                data=file_stream,
                length=file_size,
                content_type=content_type
            )
            return {
                "object_name": result.object_name,
                "etag": result.etag
            }
        except S3Error as e:
            raise Exception(f"Gagal mengunggah ke MinIO: {str(e)}")

