from fastapi import APIRouter, Depends, HTTPException, Query
import shortuuid
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.core.dependencies import get_history_service
from src.core.security import get_current_user
from src.modules.transaction.schema import TransactionPaginatedResponse
from src.modules.history.service import HistoryService
from src.models.models import History, RoleEnum, Users
from src.modules.history.schema import ActionHistoryPayload

router = APIRouter(
        prefix="/v1/history",
        tags=["History"]
    )

# ==========================================
# GET ALL HISTORY [MANAGER & USER ACCESS]
# ==========================================
@router.get("/", response_model=TransactionPaginatedResponse)
def read_history(
    userNow: Users = Depends(get_current_user), 
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100), 
    service: HistoryService = Depends(get_history_service)
):

    result = service.get_history_paginated(userNow, page, limit)
    return result

# ==========================================
# REJECT/APPROVE HISTORY [MANAGER ACCESS]
# ==========================================
@router.patch("/{id_history}")
def review_uploaded_file(
    id_history: str,
    payload: ActionHistoryPayload,
    userNow: Users = Depends(get_current_user),
    service: HistoryService = Depends(get_history_service)
):
    # Kunci Keamanan: Hanya Manager (atau role lebih tinggi) yang bisa hit ini
    if userNow.role.name not in [RoleEnum.MANAGER, RoleEnum.DIREKTUR]:
        raise HTTPException(status_code=403, detail="Akses ditolak. Hanya Manager yang dapat me-review file.")

    # Kirim ke service (termasuk id_dept Manager dari token untuk validasi)
    result_message = service.review_history(
        history_id=id_history,
        action=payload.action,
        note=payload.note,
        manager_id_dept=userNow.department_id
    )
    
    return {"status": "success", "message": result_message}


# @router.post("/migrate-uuid", tags=["System"])
# def migrate_all_tables_add_uuid(db: Session = Depends(get_db)):
#     # ==========================================
#     # 1. MIGRASI HISTORY UPLOAD
#     # ==========================================
#     try:
#         # Tambah kolom public_id
#         db.execute(text("ALTER TABLE oltp_main.history_upload ADD COLUMN public_id VARCHAR(22);"))
#         db.commit()
#     except Exception:
#         db.rollback() # Abaikan error kalau kolom ternyata sudah ada

#     # Cari data lama yang public_id-nya masih kosong, lalu isi pakai shortuuid
#     history_tanpa_uuid = db.query(HistoryUpload).filter(HistoryUpload.public_id == None).all()
#     for hist in history_tanpa_uuid:
#         hist.public_id = shortuuid.uuid()
#     db.commit()

#     try:
#         # Kunci pakai Constraint Unique & bikin Index biar cepat
#         db.execute(text("ALTER TABLE oltp_main.history_upload ADD CONSTRAINT history_public_id_unique UNIQUE (public_id);"))
#         db.execute(text("CREATE INDEX ix_history_upload_public_id ON oltp_main.history_upload (public_id);"))
#         db.commit()
#     except Exception:
#         db.rollback()