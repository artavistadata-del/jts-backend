from fastapi import APIRouter, Depends, status
import shortuuid
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.core.dependencies import get_dept_service
from src.core.security import RoleChecker, get_current_user
from src.modules.departments.service import DepartmentService
from src.models.models import Departments, Roles, Users
from src.modules.departments.schema import DepartmentsInsertSchema


router = APIRouter(
    prefix='/v1/dept',
    tags=["Department"]
)

allow_admin_only = RoleChecker(["ADMIN"])
# ==========================================
# GET ALL DEPARTMENT [ ADMIN ACCESS ]
# ==========================================
@router.get("/")
def get_all_dept(
        userNow = Depends(get_current_user),
        dept_service : DepartmentService = Depends(get_dept_service),
        user : Users = Depends(allow_admin_only)
    ):
    return dept_service.display_all_dept()

# ==========================================
# GET ADD DEPARTMENT [ADMIN ACCESS]
# ==========================================
@router.post("/", status_code=status.HTTP_201_CREATED)
def add_dept(
    dept_schema : DepartmentsInsertSchema,
    userNow = Depends(allow_admin_only),
    dept_service : DepartmentService = Depends(get_dept_service)
    
    ):
    dept_service.add_dept(dept_schema)
    return {
        "message" : "Berhasil Menambahkan Department"
    }

# ==========================================
# GET summary DEPARTMENT [ADMIN ACCESS ]
# ==========================================
@router.get("/summary", status_code=200)
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



# # @router.post("/migrate-uuid-master") # Sesuaikan path router-mu
# @router.post("/migrate-uuid-master", tags=["System"])
# def migrate_master_tables_uuid(db: Session = Depends(get_db)):
#     # 1. Update Departments Lama
#     dept_tanpa_uuid = db.query(Departments).filter(Departments.public_id == None).all()
#     for dept in dept_tanpa_uuid:
#         dept.public_id = shortuuid.uuid()
    
#     # 2. Update Roles Lama
#     roles_tanpa_uuid = db.query(Roles).filter(Roles.public_id == None).all()
#     for role in roles_tanpa_uuid:
#         role.public_id = shortuuid.uuid()
        
#     # Simpan perubahan ke database
#     db.commit()

#     return {
#         "status": "Berhasil",
#         "message": f"Update UUID selesai! {len(dept_tanpa_uuid)} Departments dan {len(roles_tanpa_uuid)} Roles berhasil diperbarui."
#     }

