from fastapi import APIRouter, Depends, HTTPException, Query, status
import shortuuid
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.core.dependencies import get_user_service
from src.core.security import RoleChecker, get_current_user
from src.models.models import Users
from src.modules.users.schema import UserMeResponse, UserSignIn as UserSchemaSignIn, UserUpdateSchema
from src.modules.users.schema import UserSignUp as UserSchemaSignUp
from src.modules.users.service import UserService


router = APIRouter(
    prefix='/v1/users',
    tags=["Users"]
)

# ==========================================
# SIGN IN
# ==========================================
@router.post("/signin")
def sign_in(userData : UserSchemaSignIn, userService : UserService = Depends(get_user_service)) :
    result = userService.signIn(userData)
    return {"message": "sign in berhasil", "data": result}

# ==========================================
# GET ME
# ==========================================
@router.get("/me", response_model=UserMeResponse)
def get_me(userNow : Users = Depends(get_current_user)):
    return {
        "status": "berhasil",
        "pesan": "Selamat datang",
        "data": userNow
    }



    
# ADMIN ONLY
allow_admin_only = RoleChecker(["ADMIN"])


# ==========================================
# SIGN UP
# ==========================================
@router.post("/signup", status_code=202)
def sign_up(userData : UserSchemaSignUp,
            userService : UserService = Depends(get_user_service),
            # userNow : Users = Depends(allow_admin_only)
    ) :
    result = userService.signUp(userData)
    return {"message": "Registrasi berhasil", "data": result}



# ==========================================
# GET ALL USER
# ==========================================
@router.get("/", status_code=200)
def get_all_users(
    page: int = Query(1, ge=1, description="Halaman yang ingin ditampilkan"),
    limit: int = Query(10, ge=1, le=100, description="Jumlah data per halaman"),
    userService: UserService = Depends(get_user_service),
    userNow: Users = Depends(allow_admin_only) 
):
    result = userService.get_all_user(page=page, limit=limit)
    return {
        "status": "berhasil",
        "message": "Data users berhasil diambil",
        "data": result["data"],
        "meta": result["meta"]
    }

# ==========================================
# GET USER BY ID
# ==========================================
@router.get("/{user_id}", response_model=UserMeResponse )
def get_me(user_id : str,
           userService : UserService = Depends(get_user_service)   
    ):
    user_data = userService.get_user_by_uuid(user_id)

    if not user_data:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    return {
        "status": "success",
        "pesan": "Berhasil mengambil data user",
        "data": user_data 
    }


# ==========================================
# UPDATE USER
# ==========================================
@router.patch("/{user_id}", status_code=200)
def update_user(
    user_id: str,
    updateData: UserUpdateSchema, 
    userService: UserService = Depends(get_user_service),
    userNow: Users = Depends(get_current_user)
):
    # result = userService.get_user_by_uuid(user_id)
    # if not result :
    #     raise HTTPException(404, 'User Tidak Ditemukan !')
    
    if userNow.roles.role != "ADMIN" and userNow.public_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kamu tidak punya akses untuk mengubah data orang lain!"
        )
    
    target_user = userService.get_user_by_uuid(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")

    # Catatan: Sesuaikan target_user.id_roles dengan nama atribut di model Users kamu
    final_id_role = updateData.id_role if userNow.roles.role == "ADMIN" else target_user.id_roles
    final_id_dept = updateData.id_dept if userNow.roles.role == "ADMIN" else target_user.id_dept

    result = userService.update_user(
        nik=target_user.nik,
        password=updateData.password,
        nama=updateData.name,
        id_role=final_id_role,
        id_dept=final_id_dept,
    )

    return {
        "status": "Berhasil",
        "message": f"Berhasil Update Data {target_user.nama}"
    }


# ==========================================
# NON ACTIVE USER
# ==========================================
@router.delete("/{id_user}", status_code=200)
def nonactive_user(
    id_user : str, 
    userService: UserService = Depends(get_user_service),
    userNow: Users = Depends(allow_admin_only)
):
    result = userService.nonactive_user(id_user)
    return {
        "status": "berhasil",
        "message": f"User dengan NIK {result['nik']} berhasil dinonaktifkan"
    }

# ==========================================
# RE ACTIVE USER
# ==========================================
@router.patch("/{id_user}/reactivate", status_code=200)
def reactivate_user_route(
    id_user: str, 
    userService: UserService = Depends(get_user_service),
    userNow: Users = Depends(allow_admin_only)
):
    result = userService.reactivate_user(id_user)
    return {
        "status": "berhasil",
        "message": f"Akun dengan NIK {result['nik']} berhasil diaktifkan kembali",
        "data": result
    }





@router.post("/migrate-uuid-manual", tags=["System"])
def migrate_users_add_uuid(db: Session = Depends(get_db)):
    # 1. ALTER TABLE: Tambahkan kolom public_id ke database
    try:
        db.execute(text("ALTER TABLE oltp_main.users ADD COLUMN public_id VARCHAR(22);"))
        db.commit()
    except Exception as e:
        db.rollback() 
        # Kalau gagal berarti kolom sudah ada, kita lanjut saja.

    # 2. ISI DATA LAMA: Cari user yang belum punya UUID
    users_tanpa_uuid = db.query(Users).filter(Users.public_id == None).all()
    
    for user in users_tanpa_uuid:
        user.public_id = shortuuid.uuid() # Generate UUID untuk user lama
        
    db.commit()

    try:
        db.execute(text("ALTER TABLE users ADD CONSTRAINT users_public_id_unique UNIQUE (public_id);"))
        db.commit()
    except Exception:
        db.rollback()

    return {
        "status": "Berhasil",
        "message": f"Berhasil menambahkan kolom dan meng-generate UUID untuk {len(users_tanpa_uuid)} user lama."
    }