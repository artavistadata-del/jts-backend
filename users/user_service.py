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
            id_dept = userSchema.id_dept
        )
        return self.user_repo.insert_user(userModels)