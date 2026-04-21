from fastapi import APIRouter, Depends
from config.dependencies import get_role_service
from core.security import get_current_user
from roles.role_service import RoleService

router = APIRouter(
    tags=["Role"]
)

@router.get("/all-role")
def get_me(userNow = Depends(get_current_user), role_service : RoleService = Depends(get_role_service)):
    return role_service.display_all_role()