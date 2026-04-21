from fastapi import APIRouter, Depends
from config.dependencies import get_dept_service
from core.security import get_current_user
from departments.department_service import DepartmentService


router = APIRouter(
    tags=["Department"]
)


@router.get("/all-dept")
def get_me(userNow = Depends(get_current_user), dept_service : DepartmentService = Depends(get_dept_service)):
    return dept_service.display_all_dept()



