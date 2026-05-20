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
from src.modules.transaction.schema import FinanceTransactionUpdate

router = APIRouter(
        prefix="/v1/transactions",
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
        result = service.get_purchasing_transactions(
            sheet_number=report_type,
            skip=page,
            limit=limit
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal server.{e}")
    

@router.get("/purchasing")
def get_purchasing_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    sheet : int = Query(1, ge=1, le=3),
    # user_now: Users = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    
    # if user_now.role.name != RoleEnum.MANAGER or user_now.role.name != RoleEnum.ADMIN:
    #     raise HTTPException(status_code=403, detail="Hanya Manager yang boleh koreksi data.")

    try:
        result = service.get_purchasing_transactions(
            sheet_number=sheet,
            skip=page,
            limit=limit
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal server.{e}")
    


@router.delete("/finance/clear")
def wipe_all_finance_transactions_endpoint(
    userNow: Users = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    """
    WARNING: Endpoint ini akan menghapus SELURUH data transaksi di Main Table Finance.
    Pastikan hanya role Admin/Superadmin yang bisa mengakses ini!
    """
    try:
        # Opsional: Jika Anda punya middleware role, pastikan userNow adalah Superadmin di sini
        result = service.wipe_all_transactions()
        return result
    except Exception as e:
        # self.db.rollback()
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal: {str(e)}")
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
    if userNow.role.role != RoleEnum.MANAGER:
        raise HTTPException(status_code=403, detail="Hanya Manager yang boleh koreksi data.")

    try:
        service.edit_transaction(
            id_dept=userNow.department_id, 
            id_fact=id_fact, 
            new_value=payload.new_value, 
            manager_nik=userNow.nik
        )
        return {"status": "success", "message": "Data berhasil dikoreksi."}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal server.")



@router.get("/finance")
def get_finance_transactions_endpoint(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    report_type: Optional[str] = Query(None, description="Filter tipe report, contoh: IS, BS"),
    # userNow: Users = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    skip = (page - 1) * limit
    
    try:
        result = service.get_finance_transactions(
            skip=skip,
            limit=limit,
            report_type=report_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal server: {e}")
    

@router.put("/finance/{id}")
def update_finance_transaction_endpoint(
    payload: FinanceTransactionUpdate,
    id: int,
    # userNow: Users = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    try:
        result = service.update_transaction_amount(
            transaction_id=id, 
            amount=payload.value
        )
        return result
    except ValueError as ve:
        # Menangkap error jika ID tidak ditemukan (dari logic Service)
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        # Menangkap error sistem lainnya
        # self.db.rollback() # Opsional, jaga-jaga jika ada transaksi nyangkut
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal server: {str(e)}")


# Endpoint DELETE
@router.delete("/finance/{id}")
def delete_finance_transaction_endpoint(
    id: int,
    # userNow: Users = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    try:
        result = service.delete_transaction_record(transaction_id=id)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        # self.db.rollback()
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal server: {str(e)}")
    


