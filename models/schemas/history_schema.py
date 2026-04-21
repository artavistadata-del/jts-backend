from datetime import date
from pydantic import BaseModel, Field

class HistoryUpload(BaseModel) :
    users_nik: str = Field(..., min_length=16, max_length=16)
    id_dept: int
    file_name: str
    time_stamp: date
    id_role : int
