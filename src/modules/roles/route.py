from fastapi import APIRouter, Depends
from src.core.dependencies import get_role_service
from src.core.security import RoleChecker, get_current_user
from src.modules.roles.service import RoleService

router = APIRouter(
    prefix='/v1/roles',
    tags=["Role"]
)
allow_admin_only = RoleChecker(["ADMIN"])
@router.get("/")
def get_me(
    userNow = Depends(allow_admin_only),
    role_service : RoleService = Depends(get_role_service)):
    return role_service.display_all_role()