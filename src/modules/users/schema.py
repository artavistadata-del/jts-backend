from typing import Optional
from pydantic import BaseModel, Field
from src.modules.departments.schema import DepartmentEnum
from src.modules.roles.schema import RolesEnum


# ==========================================================================
# INPUT
# ==========================================================================
class UserSignUp(BaseModel) :
    name : str = Field(..., max_length=255)
    nik : str = Field(..., min_length=16, max_length=16)
    password : str = Field(..., min_length=8,max_length=72)
    roles_id : str
    departments_id : str

class UserSignIn(BaseModel):
    nik: str = Field(..., min_length=16, max_length=16)
    password: str = Field(..., min_length=8)


class UserUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=8)
    password: Optional[str] = Field(None, min_length=8)
    roles_id: Optional[str] = None
    departments_id : Optional[str] = None









# ==========================================================================
# OUTPUT
# ==========================================================================
class RoleOut(BaseModel):
    id: str = Field(validation_alias="public_id")
    name: str 

    class Config:
        from_attributes = True

class DeptOut(BaseModel):
    id: str = Field(validation_alias="public_id")
    name: str

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: str = Field(validation_alias="public_id")
    name : str
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
