from pydantic import BaseModel
from typing import Optional
from datetime import date

class FactFinanceUpdate(BaseModel):
    report_type: Optional[str] = None
    idx_category: Optional[str] = None
    category: Optional[str] = None
    idx_sub_category: Optional[str] = None
    sub_category: Optional[str] = None
    sub_sub_category: Optional[str] = None
    account_name: Optional[str] = None
    bulan: Optional[date] = None
    value: Optional[float] = None