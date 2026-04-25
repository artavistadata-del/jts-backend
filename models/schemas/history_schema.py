from datetime import date
from pydantic import BaseModel, Field

class HistoryUpload(BaseModel) :
    id_users : int
    id_dept: int
    file_name: str
    time_stamp: date
    id_role : int
