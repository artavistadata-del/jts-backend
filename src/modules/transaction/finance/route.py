from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from fastapi import Query, Depends, APIRouter, HTTPException
from src.core.security import get_current_user
from src.modules.transaction.finance.dependencies import get_db, get_finance_transaction_service # Asumsi kamu punya dependency ini
from src.modules.transaction.finance.service import FinanceTransactionService
from src.modules.transaction.schema import EditTransactionRequest
from src.modules.transaction.repository import TransactionRepository
from src.models.models import Users, RoleEnum
from src.modules.transaction.schema import FinanceTransactionUpdate

router = APIRouter(
        prefix="/v1/transactions",
        tags=["Transaction"]
    )


# ==========================================
# GET ALL TRANSACTION [MANAGER ACCESS ]
# ==========================================

@router.delete("/finance/clear")
def wipe_all_finance_transactions_endpoint(
    userNow: Users = Depends(get_current_user),
    service: FinanceTransactionService = Depends(get_finance_transaction_service)
):
    """
    WARNING: Endpoint ini akan menghapus SELURUH data transaksi di Main Table Finance.
    Pastikan hanya role Admin/Superadmin yang bisa mengakses ini!
    """
    try:
        result = service.wipe_all_transactions()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal: {str(e)}")
    

@router.get("/finance/options")
def get_finance_options_endpoint(
    # userNow: Users = Depends(get_current_user),
    service: FinanceTransactionService = Depends(get_finance_transaction_service)
):
    """
    Endpoint khusus untuk mengisi dropdown filter di Frontend (Tahun & Kategori).
    """
    try:
        result = service.get_filter_options()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal server: {e}")


@router.get("/finance")
def get_finance_transactions_endpoint(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    report_type: Optional[str] = Query(None, description="Filter tipe report, contoh: IS, BS"),
    year: Optional[List[int]] = Query(None, description="Filter tahun (bisa banyak)"),
    month: Optional[List[int]] = Query(None, description="Filter bulan (bisa banyak)"),
    
    # UBAH: Kategori sekarang berupa List[str]
    category: Optional[List[str]] = Query(None, description="Filter kategori (bisa banyak), contoh: ?category=HPP&category=Kas"),
    
    search: Optional[str] = Query(None, description="Cari nama kategori menggunakan teks bebas (LIKE)"),
    
    # UBAH: Info opsi sorting yang baru
    sort_by: str = Query("year", description="Kolom sorting HANYA ADA 3: year, month, category"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Arah sorting: asc atau desc"),
    
    service: FinanceTransactionService = Depends(get_finance_transaction_service)
):
    skip = (page - 1) * limit
    
    try:
        result = service.get_finance_transactions(
            skip=skip, limit=limit, report_type=report_type,
            years=year, months=month, categories=category, # Teruskan ke service
            search=search, sort_by=sort_by, sort_order=sort_order
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal server: {e}")
    

@router.put("/finance/{id}")
def update_finance_transaction_endpoint(
    payload: FinanceTransactionUpdate,
    id: int,
    # userNow: Users = Depends(get_current_user),
    service: FinanceTransactionService = Depends(get_finance_transaction_service)
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
    service: FinanceTransactionService = Depends(get_finance_transaction_service)
):
    try:
        result = service.delete_transaction_record(transaction_id=id)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        # self.db.rollback()
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal server: {str(e)}")
    


