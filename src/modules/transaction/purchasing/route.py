from fastapi import APIRouter, Depends, Path, Query, HTTPException
from src.modules.transaction.purchasing.dependecies import get_purchasing_transaction_service
from src.modules.transaction.purchasing.service import PurchasingTransactionService


router = APIRouter(prefix="/v1/transactions", tags=["Transaction"])

@router.get("/purchasing")
def get_all_purchasing_transactions_endpoint(
    sheet_type: str = Query(
        "sheet1", 
        description="Pilih sheet data purchasing: 'sheet1', 'sheet2', atau 'sheet3'"
    ),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    service: PurchasingTransactionService = Depends(get_purchasing_transaction_service)
):
    skip = (page - 1) * limit

    try:
        result = service.get_purchasing_transactions(
            sheet_type=sheet_type.lower(), 
            skip=skip, 
            limit=limit
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Terjadi kesalahan internal server saat mengambil data: {e}",
        )
    

