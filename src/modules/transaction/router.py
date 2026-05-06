from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from fastapi import Query, Depends, APIRouter, HTTPException
from src.core.security import get_current_user
from src.core.dependencies import get_db, get_transaction_service # Asumsi kamu punya dependency ini
from src.modules.transaction.schema import EditTransactionRequest
from src.modules.transaction.repository import TransactionRepository
from src.modules.transaction.service import TransactionService
from src.models.models import Users, RoleEnum

router = APIRouter(
        prefix="/v1/transaction",
        tags=["Transaction"]
    )


# ==========================================
# GET ALL TRANSACTION [MANAGER ACCESS ]
# ==========================================
@router.get("/")
def get_department_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    report_type: Optional[str] = Query(None, description="Filter tipe report, cth: IS, BS"), # Tambahan
    userNow: Users = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    try:
        result = service.list_transactions(
            id_dept=userNow.departments_id, 
            page=page, 
            size=limit,
            user_role=userNow.roles.name,
            user_id=userNow.id,
            report_type=report_type # Passing ke service
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal server.{e}")
    

# ==========================================
# UPDATE TRANSACTION [MANAGER ACCESS ]
# ==========================================
@router.patch("/{id_fact}")
def edit_single_transaction(
    id_fact: int, 
    payload: EditTransactionRequest,
    userNow: Users = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    # 1. Kunci Keamanan: Hanya Manager yang bisa hit endpoint ini
    if userNow.roles.role != RoleEnum.MANAGER:
        raise HTTPException(status_code=403, detail="Hanya Manager yang boleh koreksi data.")

    try:
        service.edit_transaction(
            id_dept=userNow.departments_id, 
            id_fact=id_fact, 
            new_value=payload.new_value, 
            manager_nik=userNow.nik
        )
        return {"status": "success", "message": "Data berhasil dikoreksi."}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal server.")