from fastapi import APIRouter, Depends, Query
from config.dependencies import get_user_service
from core.security import get_current_user
from models.models.models import Users
from models.schemas.user_schema import UserSignIn as UserSchemaSignIn, UserUpdateSchema
from models.schemas.user_schema import UserSignUp as UserSchemaSignUp
from users.user_service import UserService


router = APIRouter(
    prefix='/users',
    tags=["Users"]
)


@router.post("/signup", status_code=202)
def sign_up(userData : UserSchemaSignUp, userService : UserService = Depends(get_user_service)) :
    result = userService.signUp(userData)
    return {"message": "Registrasi berhasil", "data": result}


@router.post("/signin")
def sign_in(userData : UserSchemaSignIn, userService : UserService = Depends(get_user_service)) :
    result = userService.signIn(userData)
    return {"message": "sign in berhasil", "data": result}


@router.get("/me")
def get_me(userNow : Users = Depends(get_current_user)):
    return {
        "status": "berhasil",
        "pesan": "Selamat datang",
        "data": {
            "nik": userNow.nik,
            "nama" : userNow.nama,
            "role" : userNow.roles.role,
            "dept" : userNow.departments.name_dept
        }
    }


@router.get("/all-user", status_code=200)
def get_all_users(
    page: int = Query(1, ge=1, description="Halaman yang ingin ditampilkan"),
    limit: int = Query(10, ge=1, le=100, description="Jumlah data per halaman"),
    userService: UserService = Depends(get_user_service),
    userNow: Users = Depends(get_current_user) 
):
    result = userService.get_all_user(page=page, limit=limit)
    return {
        "status": "berhasil",
        "message": "Data users berhasil diambil",
        "data": result["data"],
        "meta": result["meta"]
    }

@router.patch("/up-pw", status_code=200)
def update_user(
    updateData: UserUpdateSchema, 
    userService: UserService = Depends(get_user_service),
    userNow: Users = Depends(get_current_user)
):
    result = userService.update_user(
        nik=userNow.nik,
        password=updateData.password
    )
    return {
        "status": "Berhasil",
        "message": result
    }

@router.delete("/{nik}", status_code=200)
def nonactive_user(
    nik: str, 
    userService: UserService = Depends(get_user_service),
    userNow: Users = Depends(get_current_user)
):
    result = userService.nonactive_user(nik=nik)
    return {
        "status": "berhasil",
        "message": f"User dengan NIK {nik} berhasil dihapus/dinonaktifkan",
        "data": result
    }


@router.patch("/{nik}", status_code=200)
def update_user_route(
    nik: str, 
    updateData: UserUpdateSchema, 
    userService: UserService = Depends(get_user_service),
    userNow: Users = Depends(get_current_user)
):
    result = userService.update_user(
        nik=nik,
        password=updateData.password,
        id_role=updateData.id_role,
        id_dept=updateData.id_dept,
        nama= updateData.name
    )
    return {
        "status": "berhasil",
        "message": result
    }



@router.patch("/{nik}/reactivate", status_code=200)
def reactivate_user_route(
    nik: str, 
    userService: UserService = Depends(get_user_service),
    userNow: Users = Depends(get_current_user)
):
    result = userService.reactivate_user(nik=nik)
    return {
        "status": "berhasil",
        "message": f"Akun dengan NIK {nik} berhasil diaktifkan kembali",
        "data": result
    }

