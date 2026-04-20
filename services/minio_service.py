# from minio import Minio, S3Error
# import io
# from datetime import datetime
# from config.config import MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY
# from models.models import Users
# from models.schemas import HistoryUpload as HistoryUploadSchema
# from services.history_service import HistoryService


# class MinioService :
#     def __init__(self, client : Minio, user : Users, upload_service : HistoryService):
#         self.client = client
#         self.bucket_name = "finance"
#         self.user = user
#         self.history_service = upload_service

#     def upload_file(self, file_name : str, content : bytes, content_type: str) :
#         try:

#             data_stream = io.BytesIO(content)
            
#             result = self.client.put_object(
#                 bucket_name=self.bucket_name,
#                 object_name=file_name,
#                 data=data_stream,
#                 length=len(content),
#                 content_type=content_type
#             )
            
#             self._add_db(
#                 self.user.nik,
#                 self.user.id_dept,
#                 datetime.now().date(),
#                 file_name
#             )

#             return {
#                 "status": "success",
#                 "object_name": result.object_name,
#                 "etag": result.etag
#             }
            
#         except S3Error as e:
#             return {"status": "error", "message": str(e)}
        
#     def _add_db(self, nik : str, id_dept : int, time_stamp : str, file_name : str) :

#         history_schema = HistoryUploadSchema(
#            file_name=file_name,
#            users_nik= nik,
#            id_dept= id_dept,
#            time_stamp= time_stamp
#         )
#         self.history_service.add_history(history_schema=history_schema)



from minio import Minio, S3Error
from datetime import datetime, date # Pastikan import date
from config.config import MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY
from models.models import Users
from models.schemas import HistoryUpload as HistoryUploadSchema
from services.history_service import HistoryService
import typing

class MinioService:
    def __init__(self, client: Minio, user: Users, upload_service: HistoryService):
        self.client = client
        self.bucket_name = "finance"
        self.user = user
        self.history_service = upload_service

    # 1. Ubah parameter: Terima stream dan ukuran, BUKAN bytes
    def upload_file(self, file_name: str, file_stream: typing.BinaryIO, file_size: int, content_type: str):
        try:
            # Pastikan kursor pembacaan file berada di titik 0 (awal file)
            file_stream.seek(0)
            
            # 2. Lempar stream langsung ke MinIO (Zero-Copy, RAM sangat aman)
            result = self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=file_name,
                data=file_stream,
                length=file_size,
                content_type=content_type
            )
            
            self._add_db(
                self.user.nik,
                self.user.id_dept,
                datetime.now().date(),
                file_name
            )

            return {
                "status": "success",
                "object_name": result.object_name,
                "etag": result.etag
            }
            
        except S3Error as e:
            return {"status": "error", "message": str(e)}
        
    # 3. Ubah type hint time_stamp menjadi 'date', BUKAN 'str'
    def _add_db(self, nik: str, id_dept: int, time_stamp: date, file_name: str):
        history_schema = HistoryUploadSchema(
           file_name=file_name,
           users_nik=nik,
           id_dept=id_dept,
           time_stamp=time_stamp
        )
        self.history_service.add_history(history_schema=history_schema)