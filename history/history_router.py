from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from config.dependencies import get_history_service
from core.security import get_current_user
from history.history_service import HistoryService
from models.models.models import RoleEnum, Users
from models.schemas.history_schema import ActionHistoryPayload

router = APIRouter(
        prefix="/v1/history",
        tags=["History"]
    )


@router.get("/all")
def read_history(
    userNow: Users = Depends(get_current_user), 
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100), 
    service: HistoryService = Depends(get_history_service)
):

    result = service.get_history_paginated(userNow, page, limit)
    return result


# 2. Endpoint Untuk Reject/Approve
@router.post("/action/{id_history}")
def review_uploaded_file(
    id_history: int,
    payload: ActionHistoryPayload,
    userNow: Users = Depends(get_current_user),
    service: HistoryService = Depends(get_history_service)
):
    # Kunci Keamanan: Hanya Manager (atau role lebih tinggi) yang bisa hit ini
    if userNow.roles.role not in [RoleEnum.MANAGER, RoleEnum.DIREKTUR]:
        raise HTTPException(status_code=403, detail="Akses ditolak. Hanya Manager yang dapat me-review file.")

    # Kirim ke service (termasuk id_dept Manager dari token untuk validasi)
    result_message = service.review_history(
        history_id=id_history,
        action=payload.action,
        notes=payload.notes,
        manager_id_dept=userNow.id_dept
    )
    
    return {"status": "success", "message": result_message}