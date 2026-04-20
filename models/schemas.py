from datetime import date

from pydantic import BaseModel, Field
from enum import Enum

class RolesEnum(str, Enum):
    STAFF = 'STAFF'
    MANAGER = 'MANAGER'

class DepartmentEnum(str, Enum) :
    FINANCE = 'FINANCE'
    ACCOUNTING = 'ACCOUNTING'

class UserSignUp(BaseModel) :
    nik : str = Field(..., min_length=16, max_length=16)
    password : str = Field(..., min_length=8,max_length=72)
    role : RolesEnum
    department : DepartmentEnum


class UserSignIn(BaseModel):
    nik: str = Field(..., min_length=16, max_length=16)
    password: str = Field(..., min_length=8)



class HistoryUpload(BaseModel) :
    users_nik: str = Field(..., min_length=16, max_length=16)
    id_dept: int
    file_name: str
    time_stamp: date
