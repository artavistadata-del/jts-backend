from typing import Optional

from pydantic import BaseModel, Field
from models.schemas.department_schema import DepartmentEnum
from models.schemas.role_schema import RolesEnum

class UserSignUp(BaseModel) :
    nama : str = Field(..., min_length=8, max_length=255)
    nik : str = Field(..., min_length=16, max_length=16)
    password : str = Field(..., min_length=8,max_length=72)
    id_role : int
    id_dept : int

class UserSignIn(BaseModel):
    nik: str = Field(..., min_length=16, max_length=16)
    password: str = Field(..., min_length=8)


class UserUpdateSchema(BaseModel):
    password: Optional[str] = Field(None, min_length=8)
    id_role: Optional[int] = None
    id_dept: Optional[int] = None

