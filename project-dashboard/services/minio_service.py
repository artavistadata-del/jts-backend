from minio import Minio, S3Error
import io

from config.config import MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY


class MinioService :
    def __init__(self, client : Minio):
        self.client = client
        self.bucket_name = "finance"

    def upload_file(self, file_name : str, content : bytes, content_type: str) :
        try:

            data_stream = io.BytesIO(content)
            
            result = self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=file_name,
                data=data_stream,
                length=len(content),
                content_type=content_type
            )
            
            return {
                "status": "success",
                "object_name": result.object_name,
                "etag": result.etag
            }
            
        except S3Error as e:
            return {"status": "error", "message": str(e)}