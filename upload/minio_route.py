from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool 
from core.security import get_current_user 
from models.models.models import Users
from upload.minio_service import MinioService
from upload.minio_service import MinioService
from config.dependencies import get_minio_service, get_minio_service 

router = APIRouter(
    prefix='/file',
    tags=["File"]
)

@router.post("/upload-file")
async def upload_payroll_excel(
    file: UploadFile = File(...),
    userNow: Users = Depends(get_current_user),
    upload_service: MinioService = Depends(get_minio_service)
):
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(
            status_code=400, 
            detail="Format ditolak. Harap unggah file Excel (.xls atau .xlsx)"
        )

    result = await run_in_threadpool(
        upload_service.process_payroll_upload, 
        user=userNow,              
        file_name=file.filename,
        file_stream=file.file,    
        file_size=file.size,
        content_type=file.content_type
    )
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result


# from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
# from fastapi.concurrency import run_in_threadpool 
# from core.security import get_current_user 
# from models.models.models import Users

# from upload.minio_service import MinioService
# from config.dependencies import get_minio_service # Hapus import duplikat

# router = APIRouter(
#     prefix='/file',
#     tags=["File"]
# )

# @router.post("/upload-file")
# async def upload_payroll_excel(
#     file: UploadFile = File(...),
#     userNow: Users = Depends(get_current_user),
#     upload_service: MinioService = Depends(get_minio_service)
# ):
#     if not file.filename.endswith(('.xls', '.xlsx')):
#         raise HTTPException(
#             status_code=400, 
#             detail="Format ditolak. Harap unggah file Excel (.xls atau .xlsx)"
#         )

#     # Antisipasi jika file.size tidak terbaca oleh sistem
#     ukuran_file = file.size if file.size is not None else 0

#     result = await run_in_threadpool(
#         upload_service.process_payroll_upload, 
#         user=userNow,              
#         file_name=file.filename,
#         file_stream=file.file,    
#         file_size=ukuran_file,
#         content_type=file.content_type
#     )
    
#     if result.get("status") == "error":
#         raise HTTPException(status_code=500, detail=result["message"])
    
#     return result


# from fastapi import APIRouter, Depends, HTTPException, Request, Header
# from fastapi.concurrency import run_in_threadpool 
# from core.security import get_current_user 
# from models.models.models import Users

# from upload.minio_service import MinioService
# from config.dependencies import get_minio_service

# router = APIRouter(
#     prefix='/file',
#     tags=["File"]
# )

# @router.post("/upload-file")
# async def upload_payroll_excel(
#     request: Request, 
#     x_file_name: str = Header(None, alias="X-File-Name"), 
#     content_length: str = Header(None, alias="Content-Length"),
#     content_type: str = Header(None, alias="Content-Type"),
#     userNow: Users = Depends(get_current_user),
#     upload_service: MinioService = Depends(get_minio_service)
# ):
#     if not x_file_name:
#         raise HTTPException(status_code=400, detail="Header 'X-File-Name' wajib disertakan.")
    
#     # 2. Validasi ekstensi (.xls / .xlsx)
#     if not x_file_name.endswith(('.xls', '.xlsx')):
#         raise HTTPException(
#             status_code=400, 
#             detail="Format ditolak. Harap unggah file Excel (.xls atau .xlsx)"
#         )

#     # 3. Tentukan ukuran file dengan aman
#     ukuran_file = int(content_length) if content_length and content_length.isdigit() else -1

#     # 4. Lempar stream langsung ke service
#     result = await run_in_threadpool(
#         upload_service.process_payroll_upload, 
#         user=userNow,              
#         file_name=x_file_name,
#         file_stream=request.stream(), 
#         file_size=ukuran_file,
#         content_type=content_type or "application/octet-stream"
#     )
    
#     if result.get("status") == "error":
#         raise HTTPException(status_code=500, detail=result["message"])
    
#     return result