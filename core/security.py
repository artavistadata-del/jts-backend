from datetime import datetime, timedelta
import bcrypt
from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
import jwt
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from config.config import get_db
from models.models.models import Users

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/signin")

def get_password_hash(password: str) -> str:
    """Mengubah password mentah menjadi hash bcrypt"""
    pwd_bytes = password.encode('utf-8')
    
    salt = bcrypt.gensalt()
    
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
    
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Mencocokkan password dari user dengan hash di database"""
    password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)

def create_access_token(data: dict):
    """Fungsi untuk membuat KTP Digital (JWT)"""
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Fungsi ini akan mencegat request, mengambil token dari Header,
    membongkarnya, dan mencari user-nya di database PostgreSQL.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesi tidak valid atau token salah",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        nik: str = payload.get("sub")
        
        if nik is None:
            raise credentials_exception
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Waktu login habis (Token Expired), silakan login ulang."
        )
    except jwt.PyJWTError: 
        raise credentials_exception

    user = db.query(Users).filter(Users.nik == nik).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Pengguna tidak ditemukan (mungkin sudah dihapus admin)."
        )

    return user


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Users = Depends(get_current_user)):
        user_role = user.roles.role.value if user.roles and user.roles.role else None
        
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Akses ditolak. Endpoint ini hanya untuk role: {', '.join(self.allowed_roles)}"
            )
        
        return user