from fastapi import APIRouter, Depends, HTTPException, Query, status
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


@router.post("/signin")
def sign_in(userData : UserSchemaSignIn, userService : UserService = Depends(get_user_service)) :
    result = userService.signIn(userData)
    return {"message": "sign in berhasil", "data": result}


@router.get("/me", response_model=UserMeResponse)
def get_me(userNow : Users = Depends(get_current_user)):
    return {
        "status": "berhasil",
        "pesan": "Selamat datang",
        "data": userNow
    }

# ADMIN ONLY
allow_admin_only = RoleChecker(["ADMIN"])

@router.post("/signup", status_code=202)
def sign_up(userData : UserSchemaSignUp,
            userService : UserService = Depends(get_user_service),
            # userNow : Users = Depends(allow_admin_only)
    ) :
    result = userService.signUp(userData)
    return {"message": "Registrasi berhasil", "data": result}


@router.get("/all", status_code=200)
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

@router.patch("/{user_id}/update", status_code=200)
def update_user(
    user_id: int,
    updateData: UserUpdateSchema, 
    userService: UserService = Depends(get_user_service),
    userNow: Users = Depends(get_current_user)
):
    
    if userNow.roles.role != "ADMIN" and userNow.idusers != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kamu tidak punya akses untuk mengubah data orang lain!"
        )
    
    target_user = userService.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")

    result = userService.update_user(
        nik=target_user.nik,
        password=updateData.password,
        nama=updateData.name,
        id_role=updateData.id_role,
        id_dept=updateData.id_dept,
    )

    return {
        "status": "Berhasil",
        "message": f"Berhasil Update Data {target_user.nama}"
    }


@router.patch("/{id_user}/nonactive", status_code=200)
def nonactive_user(
    id_user : int, 
    userService: UserService = Depends(get_user_service),
    userNow: Users = Depends(allow_admin_only)
):
    result = userService.nonactive_user(id_user)
    return {
        "status": "berhasil",
        "message": f"User dengan NIK {result['nik']} berhasil dinonaktifkan"
    }


@router.patch("/{id_user}/reactivate", status_code=200)
def reactivate_user_route(
    id_user: int, 
    userService: UserService = Depends(get_user_service),
    userNow: Users = Depends(allow_admin_only)
):
    result = userService.reactivate_user(id_user)
    return {
        "status": "berhasil",
        "message": f"Akun dengan NIK {result['nik']} berhasil diaktifkan kembali",
        "data": result
    }

