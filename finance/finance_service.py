import math

from fastapi import Depends, HTTPException, status
from finance.finance_repository import FinanceRepository
from models.schemas.finance_schema import FactFinanceUpdate

class FinanceService:
    def __init__(self, repo: FinanceRepository):
        self.repo = repo

    def edit_finance_data(self, id_fact: int, payload: FactFinanceUpdate, id_dept : int):
        if id_dept != 1 :
            raise HTTPException(403, " Anda Tidak Memiliki akses untuk edit data ini")
        db_fact = self.repo.get_by_id(id_fact)
        if not db_fact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Data FactFinance dengan ID {id_fact} tidak ditemukan"
            )
        
        # 2. Extract payload
        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            return db_fact
            
        try:
            # 3. Lempar ke repo untuk save
            return self.repo.update(db_fact, update_data)
        except Exception as e:
            self.repo.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengupdate data: {str(e)}"
            )
    
    def get_all_finance(self, id_dept : int, page: int = 1, limit: int = 10):
        if id_dept != 1:
            raise HTTPException(403, "Anda tidak memiliki akses")
        
        if page < 1:
            page = 1
        if limit < 1:
            limit = 10
            
        skip = (page - 1) * limit
        
        total_items, finances = self.repo.select_all_finance_paginated(skip=skip, limit=limit)
        
        # Looping manual seperti gayamu di Users
        finance_list = []
        for finance in finances:
            finance_list.append({
                # "id_fact": finance.id_fact,
                "report_type": finance.report_type,
                "category": finance.category,
                "sub_category": finance.sub_category,
                "account_name": finance.account_name,
                "bulan": finance.bulan,
                "value": finance.value
            })

        total_pages = math.ceil(total_items / limit) if total_items > 0 else 0
        
        return {
            "data": finance_list,
            "meta": {
                "total_items": total_items,
                "total_pages": total_pages,
                "current_page": page,
                "limit": limit
            }
        }