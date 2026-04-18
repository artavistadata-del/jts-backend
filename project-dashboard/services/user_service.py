from fastapi import HTTPException, status
from core.security import get_password_hash, verify_password,create_access_token
from models.models import User as UserModels
from models.schemas import User as UserSchema
from repositories.user_repository import UserRepository


class UserService :
    def __init__(self, repo : UserRepository):
        self.repo = repo

    def signIn(self, userSchema : UserSchema) :
        userFind = self.repo.select_user(nik=userSchema.nik)

        if not userFind :
            raise HTTPException(404, "user tidak ditemukan")
        
        is_password_correct = verify_password(userSchema.password, userFind.hashed_password)

        if not is_password_correct:
            raise HTTPException(400, "Password salah")
        
        access_token = create_access_token(data={"sub": userFind.nik})
        
        return {"access_token": access_token, "token_type": "bearer"}
        # return "berhasil"
    
    def signUp(self, userSchema : UserSchema) :
        userFind = self.repo.select_user(nik=userSchema.nik)
        if userFind :
            raise HTTPException(400, "NIK sudah terdaftar")

        hashed_password = get_password_hash(userSchema.password)
        userModels = UserModels(
            nik = userSchema.nik,
            hashed_password = hashed_password
        )
        return self.repo.insert_user(userModels)