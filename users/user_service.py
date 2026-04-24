import math
from typing import Optional

from fastapi import HTTPException, status
from core.security import get_password_hash, verify_password,create_access_token
from departments.department_service import DepartmentService
from models.models.models import Users as UserModels
from models.schemas.user_schema import UserSignUp as UserSchemaSignUp
from models.schemas.user_schema import UserSignIn as UserSchemaSignIn

from roles.role_service import RoleService
from users.user_repository import UserRepository


class UserService :
    def __init__(self, user_repo : UserRepository, role_service : RoleService, dept_service : DepartmentService):
        self.user_repo = user_repo
        self.role_service = role_service
        self.dept_service = dept_service

    def signIn(self, userSchema : UserSchemaSignIn) :
        userFind = self.user_repo.select_user(nik=userSchema.nik)

        if not userFind :
            raise HTTPException(404, "user tidak ditemukan")

        if userFind.is_active == False :
            raise HTTPException(400, 'akun di non aktifkan')
        
        is_password_correct = verify_password(userSchema.password, userFind.password)

        if not is_password_correct:
            raise HTTPException(400, "Password salah")
        
        access_token = create_access_token(data={"sub": userFind.nik})
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    def signUp(self, userSchema : UserSchemaSignUp) :
        userFind = self.user_repo.select_user(nik=userSchema.nik)
        if userFind :
            raise HTTPException(302, "NIK sudah terdaftar")

        hashed_password = get_password_hash(userSchema.password)

        roleFind = self.role_service.display_role_by_id(userSchema.id_role)

        if not roleFind :
            raise HTTPException(404, 'Role tidak terdaftar')
        
        deptFind = self.dept_service.display_dept_by_id(userSchema.id_dept)

        if not deptFind :
            raise HTTPException(404, 'Department tidak terdaftar')

        userModels = UserModels(
            nik = userSchema.nik,
            password = hashed_password,
            id_roles = userSchema.id_role,
            id_dept = userSchema.id_dept,
            nama = userSchema.nama
        )
        return self.user_repo.insert_user(userModels)
    
    def get_all_user(self, page: int = 1, limit: int = 10):
        if page < 1:
            page = 1
        if limit < 1:
            limit = 10
            
        skip = (page - 1) * limit
        
        total_items, users = self.user_repo.select_all_user_paginated(skip=skip, limit=limit)
        
        user_list = []
        for user in users:
            user_list.append({
                "nik": user.nik,
                "name" : user.nama,
                "is_active": user.is_active,
                "role": {
                    "id": user.id_roles,
                    "name": user.roles.role.value if user.roles and user.roles.role else None 
                },
                "department": {
                    "id": user.id_dept,
                    "name": user.departments.name_dept if user.departments else None
                }
            })

        total_pages = math.ceil(total_items / limit) if total_items > 0 else 0
        
        return {
            "data": user_list,
            "meta": {
                "total_items": total_items,
                "total_pages": total_pages,
                "current_page": page,
                "limit": limit
            }
        }
    

    def nonactive_user(self, nik: str):
        userFind = self.user_repo.select_user(nik=nik)
        if not userFind:
            raise HTTPException(status_code=404, detail="User tidak ditemukan")
        
        if not userFind.is_active:
            raise HTTPException(status_code=400, detail="User sudah dalam keadaan non-aktif")

        is_deleted = self.user_repo.deactivate_user(nik)
        
        if not is_deleted:
            raise HTTPException(status_code=500, detail="Gagal menonaktifkan user")

        return {"nik": nik, "status": "non-aktif"}
    

    def update_user(self, nik: str, password: Optional[str] = None, 
                    id_role: Optional[int] = None, id_dept: Optional[int] = None, nama : Optional[str] = None):
        print(nik)
        user = self.user_repo.select_user(nik)
        if not user:
            raise HTTPException(404, "User tidak ditemukan")

        if password:
            user.password = get_password_hash(password)

        if id_role:
            role_find = self.role_service.display_role_by_id(id_role)
            if not role_find:
                raise HTTPException(404, "Role tidak ditemukan")
            user.id_roles = id_role

        if id_dept:
            dept_find = self.dept_service.display_dept_by_id(id_dept)
            if not dept_find:
                raise HTTPException(404, "Department tidak ditemukan")
            user.id_dept = id_dept

        if nama :
            user.nama = nama
        print(nik)
        return self.user_repo.update_user(user)
    

    def reactivate_user(self, nik: str):
        userFind = self.user_repo.select_user(nik=nik)
        if not userFind:
            raise HTTPException(status_code=404, detail="User tidak ditemukan")
        
        if userFind.is_active:
            raise HTTPException(status_code=400, detail="User ini sudah dalam keadaan aktif")

        is_reactivated = self.user_repo.reactivate_user(nik)
        
        if not is_reactivated:
            raise HTTPException(status_code=500, detail="Gagal mengaktifkan kembali user")

        return {"nik": nik, "status": "aktif"}