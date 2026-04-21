from fastapi import APIRouter, Depends

# Import yang dibutuhkan (sesuaikan dengan struktur foldermu)
from config.dependencies import get_user_service
from core.security import get_current_user
from models.schemas.user_schema import UserSignIn as UserSchemaSignIn
from models.schemas.user_schema import UserSignUp as UserSchemaSignUp
from users.user_service import UserService


router = APIRouter(
    prefix='/display',
    tags=["Display"]
)


@router.get("/signup", status_code=202)
def sign_up(userData : UserSchemaSignUp, userService : UserService = Depends(get_user_service)) :
    result = userService.signUp(userData)
    return {"message": "Registrasi berhasil", "data": result}



