from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

from src.models.models import StatusEnum

class HistoryUpload(BaseModel) :
    users_id : int
    departments_id: int
    file_name: str
    time_stamp: date
    roles_id : int
    file_name_storage : str


class ActionHistoryPayload(BaseModel):
    action: StatusEnum
    notes: Optional[str] = None