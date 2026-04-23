from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from cleaning.tasks import process_cleaning_task
from core.security import get_current_user 
from departments.department_service import DepartmentService
from models.models.models import Users
from upload.minio_service import MinioService
from upload.minio_service import MinioService
from config.dependencies import get_dept_service, get_minio_service, get_minio_service 

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
    
    # return result.get('data')

    process_cleaning_task.delay(result.get('data')[0], result.get('data')[1], userNow.id_dept)

    return 'berhasil'



