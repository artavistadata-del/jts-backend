from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.security import get_current_user
from config.dependencies import get_db, get_transaction_service # Asumsi kamu punya dependency ini
from models.schemas.transaction_schema import EditTransactionRequest
from transaction.transaction_repository import TransactionRepository
from transaction.transaction_service import TransactionService
from models.models.models import Users, RoleEnum

router = APIRouter(
        prefix="/v1/transaction",
        tags=["Transaction"]
    )


@router.get("/list")
def get_department_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    userNow: Users = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):

    try:
        result = service.list_transactions(
            id_dept=userNow.id_dept, 
            page=page, 
            size=limit,
            user_role=userNow.roles.role,
            user_id=userNow.idusers
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal server.{e}")
    


@router.patch("/edit/{id_fact}")
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
            id_dept=userNow.id_dept, 
            id_fact=id_fact, 
            new_value=payload.new_value, 
            manager_nik=userNow.nik
        )
        return {"status": "success", "message": "Data berhasil dikoreksi."}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal server.")