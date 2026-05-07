from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

from src.models.models import StatusEnum

class HistoryUpload(BaseModel) :
    user_id : int
    department_id: int
    file_name: str
    time_stamp: date
    role_id : int
    file_name_storage : str
    status: StatusEnum = StatusEnum.ANALYZING


class ActionHistoryPayload(BaseModel):
    action: StatusEnum
    note: Optional[str] = None