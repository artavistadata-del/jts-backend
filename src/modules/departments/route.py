from fastapi import APIRouter, Depends
from src.config.dependencies import get_dept_service
from src.core.security import RoleChecker, get_current_user
from src.modules.departments.service import DepartmentService
from src.models.models.models import Users
from src.modules.departments.schema import DepartmentsInsertSchema


router = APIRouter(
    prefix='/v1/dept',
    tags=["Department"]
)

allow_admin_only = RoleChecker(["ADMIN"])

@router.get("/all-dept")
def get_all_dept(
        userNow = Depends(get_current_user),
        dept_service : DepartmentService = Depends(get_dept_service),
        user : Users = Depends(allow_admin_only)
    ):
    return dept_service.display_all_dept()

@router.post("/add-dept")
def add_dept(
    dept_schema : DepartmentsInsertSchema,
    userNow = Depends(allow_admin_only),
    dept_service : DepartmentService = Depends(get_dept_service)
    
    ):
    dept_service.add_dept(dept_schema)
    return {
        "message" : "Berhasil Menambahkan Department"
    }


@router.get("/dept-sum", status_code=200)
def get_dept_summary(
        deptService: DepartmentService = Depends(get_dept_service),
        user : Users = Depends(allow_admin_only)
    ):
    result = deptService.get_department_staff_summary()
    
    return {
        "status": "berhasil",
        "message": "Data jumlah staff per departemen berhasil diambil",
        "data": result
    }

