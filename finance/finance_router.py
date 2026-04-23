from fastapi import APIRouter, Depends, Query
from config.dependencies import get_finance_service
from core.security import get_current_user
from finance.finance_service import FinanceService
from models.models.models import Users
from models.schemas.finance_schema import FactFinanceUpdate

router = APIRouter(prefix="/finance", tags=["Finance"])

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