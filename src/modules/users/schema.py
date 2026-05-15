from typing import Optional
from pydantic import BaseModel, Field
from src.modules.departments.schema import DepartmentEnum
from src.modules.roles.schema import RolesEnum


# ==========================================================================
# DTO INPUT
# ==========================================================================
class UserSignUp(BaseModel) :
    name : str = Field(..., max_length=255)
    nik : str = Field(..., min_length=16, max_length=16)
    password : str = Field(..., min_length=8,max_length=72)
    role_id : str
    department_id : str

class UserSignIn(BaseModel):
    nik: str = Field(..., min_length=16, max_length=16)
    password: str = Field(..., min_length=8)


class UserUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=8)
    password: Optional[str] = Field(None, min_length=8)
    role_id: Optional[str] = None
    department_id : Optional[str] = None


class UserUpdatePasswordPayload(BaseModel) :
    current_password : str = Field(None, min_length=8)
    new_password : str = Field(None, min_length=8)
    confirm_new_password : str = Field(None, min_length=8)









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
    department : DeptOut
    role : RoleOut
    
    class Config:
        from_attributes = True

class UserMeResponse(BaseModel):
    status: str
    pesan: str
    data: UserOut

# from typing import Optional
# from pydantic import BaseModel, Field

# # ==========================================================================
# # INPUT (REQUESTS) - Menggunakan akhiran aksi: Create, Login, Update
# # ==========================================================================

# # Sebelumnya: UserSignUp
# class UserCreate(BaseModel):
#     name: str = Field(..., max_length=255)
#     nik: str = Field(..., min_length=16, max_length=16)
#     password: str = Field(..., min_length=8, max_length=72)
#     role_id: str
#     department_id: str

# # Sebelumnya: UserSignIn
# class UserLogin(BaseModel):
#     nik: str = Field(..., min_length=16, max_length=16)
#     password: str = Field(..., min_length=8)

# # Sebelumnya: UserUpdateSchema
# class UserUpdate(BaseModel):
#     name: Optional[str] = Field(None, min_length=8)
#     password: Optional[str] = Field(None, min_length=8)
#     role_id: Optional[str] = None
#     department_id: Optional[str] = None

# # Sebelumnya: UserUpdatePasswordPayload
# class UserPasswordUpdate(BaseModel):
#     current_password: str = Field(None, min_length=8)
#     new_password: str = Field(None, min_length=8)
#     confirm_new_password: str = Field(None, min_length=8)


# # ==========================================================================
# # OUTPUT (RESPONSES) - Menggunakan akhiran "Response"
# # ==========================================================================

# # Sebelumnya: RoleOut
# class RoleResponse(BaseModel):
#     id: str = Field(validation_alias="public_id")
#     name: str 

#     class Config:
#         from_attributes = True

# # Sebelumnya: DeptOut (Jangan disingkat)
# class DepartmentResponse(BaseModel):
#     id: str = Field(validation_alias="public_id")
#     name: str

#     class Config:
#         from_attributes = True

# # Sebelumnya: UserOut
# class UserResponse(BaseModel):
#     id: str = Field(validation_alias="public_id")
#     name: str
#     nik: str
#     is_active: bool
#     department: DepartmentResponse
#     role: RoleResponse
    
#     class Config:
#         from_attributes = True

# # Sebelumnya: UserMeResponse (Tetap menggunakan Response, tapi dikhususkan)
# class UserProfileResponse(BaseModel):
#     status: str
#     pesan: str
#     data: UserResponse