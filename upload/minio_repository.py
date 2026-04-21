from minio import Minio, S3Error
import typing

class MinioRepository:
    def __init__(self, client: Minio):
        self.client = client
        self.bucket_name = "finance"

    def upload_file(self, file_name: str, file_stream: typing.BinaryIO, file_size: int, content_type: str):
        """Hanya bertugas mengirim file fisik ke MinIO"""
        try:
            file_stream.seek(0) 
            
            result = self.client.put_object(
                bucket_name=self.bucket_name,
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



# from minio import Minio, S3Error
# import typing

# class MinioRepository:
#     def __init__(self, client: Minio):
#         self.client = client
#         self.bucket_name = "finance"

#     def upload_file(self, file_name: str, file_stream: typing.BinaryIO, file_size: int, content_type: str):
#         """Hanya bertugas mengirim file fisik ke MinIO"""
#         try:
#             file_stream.seek(0) 
            
#             result = self.client.put_object(
#                 bucket_name=self.bucket_name,
#                 object_name=file_name,
#                 data=file_stream,
#                 # --- SOLUSI FILE BESAR (ANTI-LAG) ---
#                 length=-1, # Beri tahu MinIO untuk membaca sampai file benar-benar habis
#                 part_size=10 * 1024 * 1024, # Pecah aliran data menjadi 10MB per bagian
#                 content_type=content_type
#             )
#             return {
#                 "object_name": result.object_name,
#                 "etag": result.etag
#             }
#         except S3Error as e:
#             raise Exception(f"Gagal mengunggah ke MinIO: {str(e)}")