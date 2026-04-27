from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

from models.models.models import StatusEnum

class HistoryUpload(BaseModel) :
    id_users : int
    id_dept: int
    file_name: str
    time_stamp: date
    id_role : int


class ActionHistoryPayload(BaseModel):
    action: StatusEnum
    notes: Optional[str] = None