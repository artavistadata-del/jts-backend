from pydantic import BaseModel, Field
from models.schemas.department_schema import DepartmentEnum
from models.schemas.role_schema import RolesEnum

class UserSignUp(BaseModel) :
    nik : str = Field(..., min_length=16, max_length=16)
    password : str = Field(..., min_length=8,max_length=72)
    role : RolesEnum
    department : DepartmentEnum

class UserSignIn(BaseModel):
    nik: str = Field(..., min_length=16, max_length=16)
    password: str = Field(..., min_length=8)

