from typing import Optional

from pydantic import BaseModel, Field
from models.schemas.department_schema import DepartmentEnum
from models.schemas.role_schema import RolesEnum


# ==========================================================================
# INPUT
# ==========================================================================
class UserSignUp(BaseModel) :
    nama : str = Field(..., max_length=255)
    nik : str = Field(..., min_length=16, max_length=16)
    password : str = Field(..., min_length=8,max_length=72)
    id_role : int
    id_dept : int

class UserSignIn(BaseModel):
    nik: str = Field(..., min_length=16, max_length=16)
    password: str = Field(..., min_length=8)


class UserUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=8)
    password: Optional[str] = Field(None, min_length=8)
    id_role: Optional[int] = None
    id_dept: Optional[int] = None








# ==========================================================================
# OUTPUT
# ==========================================================================
class RoleOut(BaseModel):
    id_roles: int
    role: str 

    class Config:
        from_attributes = True

class DeptOut(BaseModel):
    id_dept: int
    name_dept: str

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    idusers: int = Field(validation_alias="idusers")
    id_dept : int
    nama : str
    nik : str
    id_roles : int
    is_active : bool
    departments : DeptOut
    roles : RoleOut
    
    class Config:
        from_attributes = True

class UserMeResponse(BaseModel):
    status: str
    pesan: str
    data: UserOut
