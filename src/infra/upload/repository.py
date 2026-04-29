from minio import Minio, S3Error
import typing

from src.config.dept_registry import get_dept_config

class UploadRepository:
    def __init__(self, client: Minio):
        self.client = client


    def upload_file(self, file_name: str, file_stream: typing.BinaryIO, file_size: int, content_type: str, dept_id : int):
        """Hanya bertugas mengirim file fisik ke MinIO"""
        # bucket_name = f"raw-dept-{dept_id}"
        bucket_name = get_dept_config(dept_id)
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

