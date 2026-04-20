from fastapi import HTTPException, status
from core.security import get_password_hash, verify_password,create_access_token
from models.models import Users as UserModels
from models.schemas import UserSignUp as UserSchemaSignUp
from models.schemas import UserSignIn as UserSchemaSignIn
from repositories.department_repository import DepartmentRepository
from repositories.role_repository import RoleRepository
from repositories.user_repository import UserRepository


class UserService :
    def __init__(self, user_repo : UserRepository, role_repo : RoleRepository, dept_repo : DepartmentRepository):
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.dept_repo = dept_repo

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


        roleFind = self.role_repo.select_role_by_role(userSchema.role)

        if not roleFind :
            raise HTTPException(404, 'Role tidak terdaftar')
        
        deptFind = self.dept_repo.select_dept_by_dept(userSchema.department)

        if not roleFind :
            raise HTTPException(404, 'Department tidak terdaftar')

        userModels = UserModels(
            nik = userSchema.nik,
            password = hashed_password,
            id_roles = roleFind[0],
            id_dept = deptFind[0]
        )
        return self.user_repo.insert_user(userModels)