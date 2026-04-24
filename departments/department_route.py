from fastapi import APIRouter, Depends
from config.dependencies import get_dept_service
from core.security import get_current_user
from departments.department_service import DepartmentService
from models.schemas.department_schema import DepartmentsInsertSchema


router = APIRouter(
    tags=["Department"]
)


@router.get("/all-dept")
def get_all_dept(userNow = Depends(get_current_user), dept_service : DepartmentService = Depends(get_dept_service)):
    return dept_service.display_all_dept()

@router.post("/add-dept")
def add_dept(
    dept_schema : DepartmentsInsertSchema,
    userNow = Depends(get_current_user),
    dept_service : DepartmentService = Depends(get_dept_service)
    
    ):
    dept_service.add_dept(dept_schema)
    return {
        "message" : "Berhasil Menambahkan Department"
    }


@router.get("/staff-summary", status_code=200)
def get_staff_summary(deptService: DepartmentService = Depends(get_dept_service)):
    result = deptService.get_department_staff_summary()
    
    return {
        "status": "berhasil",
        "message": "Data jumlah staff per departemen berhasil diambil",
        "data": result
    }

