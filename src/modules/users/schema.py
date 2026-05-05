from typing import Optional

from pydantic import BaseModel, Field
from src.modules.departments.schema import DepartmentEnum
from src.modules.roles.schema import RolesEnum


# ==========================================================================
# INPUT
# ==========================================================================
class UserSignUp(BaseModel) :
    nama : str = Field(..., max_length=255)
    nik : str = Field(..., min_length=16, max_length=16)
    password : str = Field(..., min_length=8,max_length=72)
    id_role : str
    id_dept : str

class UserSignIn(BaseModel):
    nik: str = Field(..., min_length=16, max_length=16)
    password: str = Field(..., min_length=8)


class UserUpdateSchema(BaseModel):
    nama: Optional[str] = Field(None, min_length=8)
    password: Optional[str] = Field(None, min_length=8)
    id_role: Optional[str] = None
    id_dept: Optional[str] = None









# ==========================================================================
# OUTPUT
# ==========================================================================
class RoleOut(BaseModel):
    id_roles: int
    role_name: str = Field(validation_alias="role")

    class Config:
        from_attributes = True

class DeptOut(BaseModel):
    id_dept: int
    name_dept: str

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id_user: str = Field(validation_alias="public_id")
    nama : str
    nik : str
    is_active : bool
    departments : DeptOut
    roles : RoleOut
    
    class Config:
        from_attributes = True

class UserMeResponse(BaseModel):
    status: str
    pesan: str
    data: UserOut
