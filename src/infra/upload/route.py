from datetime import datetime
from fastapi import Form
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from src.core.security import get_current_user 
from src.infra.upload.schema import ConfirmRequest, ConfirmUploadInput
from src.modules.departments.service import DepartmentService
from src.modules.history.service import HistoryService
from src.models.models import RoleEnum, StatusEnum, Users
from src.infra.upload.service import UploadService
from src.infra.upload.service import UploadService
from src.core.dependencies import get_dept_service, get_history_service, get_minio_service, get_minio_service 

router = APIRouter(
    prefix='/v1/uploads',
    tags=["Upload"]
)


# ==========================================
# UPLOAD FILE [ USER ACCESS ]
# ==========================================
@router.post("/xxx")
async def upload_payroll_excel(
    file: UploadFile = File(...),
    userNow: Users = Depends(get_current_user),
    upload_service: UploadService = Depends(get_minio_service)
):
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(
            status_code=403, 
            detail="Format ditolak. Harap unggah file Excel (.xls atau .xlsx)"
        )
    
    # if userNow.role.name == 'ADMIN' or userNow.role.name == 'DIREKTUR' :
    #     raise HTTPException(
    #         status_code=403, 
    #         detail="Akses ditolak. Role Anda Tidak Punya akses Upload File"
    #     )
    
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

# ==========================================
# UPLOAD FILE [ DINAMIS MULTI-DEPT ]
# ==========================================
@router.post("/")
async def upload_payroll_excel(
    file: UploadFile = File(...),
    target_dept_id: Optional[str] = Form(None),
    userNow: Users = Depends(get_current_user),
    upload_service: UploadService = Depends(get_minio_service),
):
    
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(
            status_code=400, 
            detail="Format ditolak. Harap unggah file Excel (.xls atau .xlsx)"
        )
    
    result = await run_in_threadpool(
        upload_service.process_payroll_upload,               
        file_name=file.filename,
        file_stream=file.file,    
        file_size=file.size,
        content_type=file.content_type,
        target_dept_id=target_dept_id,
        userNow=userNow
    )
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result

# ==========================================
# GET STATUS HISTORY -> STATUS CHECK [ USER ACCESS ]
# ==========================================
@router.get("/{history_id}")
def get_upload_status(
        history_id: str,
        history_service : HistoryService = Depends(get_history_service),
        userNow: Users = Depends(get_current_user)
    ):
    record = history_service.get_history_by_uuid(history_id)
    
    if not record:
        raise HTTPException(status_code=404, detail="Data history tidak ditemukan.")
    
    if record.user_id != userNow.id and userNow.role.name != RoleEnum.ADMIN.value:
        raise HTTPException(
            status_code=403, 
            detail="Akses ditolak. Anda tidak dapat melihat status milik pengguna lain."
        )

    if record.status == StatusEnum.FAILED:
        error_msg = record.analysis_result.get("error") if record.analysis_result else "Unknown error"
        
        raise HTTPException(
            status_code=422, 
            detail={
                "history_id": record.public_id,
                "status": record.status,
                "error_detail": error_msg
            }
        )

    response = {
        "history_id": record.public_id,
        "status": record.status,
    }

    if record.status == StatusEnum.AWAITING_PREVIEW:
        response["preview_data"] = record.analysis_result
    
    return response

# ==========================================
# CONFIRM HISTORY -> Confirm From User [ USER ACCESS ]
# ==========================================
@router.post("/{history_id}/confirm")
def confirm_upload(
        history_id: str,
        action : ConfirmRequest,
        history_service : HistoryService = Depends(get_history_service),
        userNow: Users = Depends(get_current_user)
    ):

    
    record = history_service.get_history_by_uuid(history_id)
    

    if not record:
        raise HTTPException(status_code=404, detail="Data history tidak ditemukan.")
    
    if record.user_id != userNow.id:
        raise HTTPException(
            status_code=403, 
            detail="Akses ditolak. Anda tidak diizinkan memproses data milik pengguna lain."
        )

    history_service.confirm_and_process_upload(record.id, action.action)

    return {
        "status": "success", 
        "message": "Berhasil Melakukan Aksi"
    }


