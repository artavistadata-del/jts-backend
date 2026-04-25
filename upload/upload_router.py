from datetime import datetime
from uuid import uuid4
from celery import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session
from cleaning.tasks import analyze_excel_task, commit_upsert_task
from config.config import get_db
from config.dependencies import get_finance_service
from core.security import get_current_user
from finance.finance_service import FinanceService
from models.models.models import HistoryUpload, StatusEnum, Users
from models.schemas.finance_schema import FactFinanceUpdate
from config.minio_conf import minio_client

router = APIRouter(prefix="/up", tags=["UP"])
@router.patch("/{id_fact}")
def update_fact_finance(
    id_fact: int,
    payload: FactFinanceUpdate,
    service: FinanceService = Depends(get_finance_service),
    userNow : Users = Depends(get_current_user)
):
    updated_data = service.edit_finance_data(id_fact, payload, userNow.id_dept)
    
    return {
        "status": "success",
        "message": "Data berhasil diubah"
        # "data": updated_data
    }


@router.get("/all-finance", status_code=200)
def get_all_finances(
    page: int = Query(1, ge=1, description="Halaman yang ingin ditampilkan"),
    limit: int = Query(10, ge=1, le=100, description="Jumlah data per halaman"),
    financeService: FinanceService = Depends(get_finance_service),
    userNow : Users = Depends(get_current_user)
):
    result = financeService.get_all_finance(page=page, limit=limit, id_dept=userNow.id_dept)
    return {
        "status": "berhasil",
        "message": "Data finance berhasil diambil",
        "data": result["data"],
        "meta": result["meta"]
    }

# Di dalam api/finance_router.py

@router.get("/status/{history_id}")
def check_upload_status(history_id: int, db: Session = Depends(get_db)):
    record = db.query(HistoryUpload).filter(HistoryUpload.id_history_upload == history_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan.")

    response_data = {
        "history_id": record.id_history_upload,
        "status": record.status,
    }

    # INI BAGIAN PENTING UNTUK FE:
    # Jika analisis selesai, kirimkan hasil hitungan Polars ke FE
    if record.status == StatusEnum.AWAITING_PREVIEW:
        # analysis_result berisi dict: {"total_insert": 150, "total_replace": 50, "dept_name": "Finance"}
        response_data["preview_data"] = record.analysis_result 
    
    elif record.status in [StatusEnum.REJECTED, StatusEnum.REJECTED]:
        response_data["error"] = record.analysis_result.get("error", "Terjadi kesalahan sistem.")

    return response_data


# ==========================================
# 1. ENDPOINT UPLOAD (Inisiasi Fase 1)
# ==========================================
@router.post("/upload")
async def upload_finance_data(
    file: UploadFile = File(...),
    userNow : Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validasi format file
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Format file harus Excel (.xlsx atau .xls).")

    # Generate nama file unik untuk mencegah bentrok di MinIO
    file_ext = file.filename.split(".")[-1]
    safe_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}.{file_ext}"
    bucket_name = f"raw-dept-{userNow.id_dept}"
    
    try:

        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            
        minio_client.put_object(
            bucket_name, safe_filename, file.file, length=-1, part_size=10*1024*1024
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal upload ke MinIO: {str(e)}")

    new_history = HistoryUpload(
        # users_nik=users_nik,
        users_nik=userNow.nik,
        # id_dept=id_dept,
        id_dept=userNow.id_dept,
        id_roles=1, # Default role STAFF
        file_name=safe_filename,
        status=StatusEnum.ANALYZING
    )
    db.add(new_history)
    db.commit()
    db.refresh(new_history)

    # Pemicu Celery Task 1 (Analisis/Preview) secara asinkron
    analyze_excel_task.delay(new_history.id_history_upload, safe_filename, userNow.id_dept)

    return {
        "status": "success",
        "history_id": new_history.id_history_upload,
        "message": "Analisis data dimulai."
    }

# ==========================================
# 2. ENDPOINT STATUS (Polling untuk FE)
# ==========================================
@router.get("/status/{history_id}")
def get_upload_status(history_id: int, db: Session = Depends(get_db)):
    record = db.query(HistoryUpload).filter(HistoryUpload.id_history_upload == history_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Data history tidak ditemukan.")

    response = {
        "history_id": record.id_history_upload,
        "status": record.status,
    }

    # Kirim data preview jika analisis Polars sudah selesai
    if record.status == StatusEnum.AWAITING_PREVIEW:
        response["preview_data"] = record.analysis_result
    
    elif record.status == StatusEnum.FAILED:
        response["error_detail"] = record.analysis_result.get("error") if record.analysis_result else "Unknown error"

    return response

# ==========================================
# 3. ENDPOINT CONFIRM (Inisiasi Fase 2)
# ==========================================
@router.post("/confirm/{history_id}")
def confirm_upload(history_id: int, db: Session = Depends(get_db)):
    record = db.query(HistoryUpload).filter(HistoryUpload.id_history_upload == history_id).first()
    
    if not record or record.status != StatusEnum.AWAITING_PREVIEW:
        raise HTTPException(status_code=400, detail="Status data tidak valid untuk konfirmasi.")

    # Ubah status ke PROCESSING_INSERT agar FE tahu proses simpan dimulai
    record.status = StatusEnum.PROCESSING_INSERT
    db.commit()

    # Pemicu Celery Task 2 (Upsert permanen)
    commit_upsert_task.delay(history_id, record.file_name, record.id_dept)

    return {"status": "success", "message": "Proses penyimpanan permanen dimulai."}