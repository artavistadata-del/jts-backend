from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from cleaning.tasks import analyze_excel_task
# from cleaning.tasks import analyze_excel_task, process_cleaning_task
from core.security import get_current_user 
from departments.department_service import DepartmentService
from history.history_service import HistoryService
from models.models.models import StatusEnum, Users
from upload.minio_service import MinioService
from upload.minio_service import MinioService
from config.dependencies import get_dept_service, get_history_service, get_minio_service, get_minio_service 

router = APIRouter(
    prefix='/v1/upload',
    tags=["Upload"]
)

@router.post("/file")
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


@router.get("/status/{history_id}")
def get_upload_status(
        history_id: int,
        history_service : HistoryService = Depends(get_history_service),
        userNow: Users = Depends(get_current_user)
    ):
    record = history_service.get_history_by_id(history_id)
    
    if not record:
        raise HTTPException(status_code=404, detail="Data history tidak ditemukan.")
    
    if record.id_users != userNow.idusers:
        raise HTTPException(
            status_code=403, 
            detail="Akses ditolak. Anda tidak dapat melihat status milik pengguna lain."
        )

    response = {
        "history_id": record.id_history_upload,
        "status": record.status,
    }

    if record.status == StatusEnum.AWAITING_PREVIEW:
        response["preview_data"] = record.analysis_result
    
    elif record.status == StatusEnum.FAILED:
        response["error_detail"] = record.analysis_result.get("error") if record.analysis_result else "Unknown error"

    return response

@router.post("/confirm/{history_id}")
def confirm_upload(
        history_id: int,
        history_service : HistoryService = Depends(get_history_service),
        userNow: Users = Depends(get_current_user)
    ):

    
    record = history_service.get_history_by_id(history_id)
    

    if not record:
        raise HTTPException(status_code=404, detail="Data history tidak ditemukan.")
    
    if record.id_users != userNow.idusers:
        raise HTTPException(
            status_code=403, 
            detail="Akses ditolak. Anda tidak diizinkan memproses data milik pengguna lain."
        )

    history_service.confirm_and_process_upload(history_id)

    return {
        "status": "success", 
        "message": "Proses penyimpanan permanen dimulai."
    }


