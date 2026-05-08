from fastapi import HTTPException

from src.modules.departments.repository import DepartmentRepository
from src.models.models import Departments
from src.modules.departments.schema import DepartmentsInsertSchema, DepartmentsUpdateSchema


class DepartmentService :
    def __init__(self, dept_repo : DepartmentRepository):
        self.repo = dept_repo

    # ==========================================
    # GET DEPT BY DEPT [ADMIN ACCESS ]
    # ==========================================
    def display_dept_by_dept(self, name : str) :
        return self.repo.get_dept_by_dept(name)
    
    # ==========================================
    # GET DEPT BY ID [ADMIN ACCESS ]
    # ==========================================
    def display_dept_by_id(self, id_dept : int) :
        return self.repo.get_dept_by_id(id_dept)
    
    # ==========================================
    # GET DEPT BY UUID [ADMIN ACCESS ]
    # ==========================================
    def display_dept_by_uuid(self, id_dept : str) :
        return self.repo.get_dept_by_uuid(id_dept)
    
    # ==========================================
    # GET ALL DEPT [ADMIN ACCESS ]
    # ==========================================
    def display_all_dept(self, sort_by: str = "name", sort_order: str = "asc"):

        if sort_by not in ["name"]:
            raise HTTPException(400, "Kolom pengurutan tidak valid")
        
        if sort_order.lower() not in ["asc", "desc"]:
            raise HTTPException(400, "Arah pengurutan tidak valid")

        dept_find = self.repo.get_all_dept(sort_by=sort_by, sort_order=sort_order)
        
        if not dept_find:
            raise HTTPException(404, "Belum Ada Department")
        
        hasil_format = []
        for r in dept_find:
            hasil_format.append({
                "id": r.public_id,
                "name": r.name
            })
        
        return {
            "message": "Berhasil mengambil data department",
            "data": hasil_format,
            "meta": {
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        }
    
    # ==========================================
    # ADD DEPT [ADMIN ACCESS ]
    # ==========================================
    def add_dept(self, dept : DepartmentsInsertSchema) :
        find_dept = self.display_dept_by_dept(dept.name.upper())

        if find_dept :
            raise HTTPException(409, " Department Sudah Ada")

        dept_model = Departments(
                name = dept.name
        )
        return self.repo.insert_dept(dept_model)

    # ==========================================
    # GET DEPT WITH SUMMARY  [ADMIN ACCESS ]
    # ==========================================
    def get_department_staff_summary(self):
        data = self.repo.get_staff_count_per_dept()
        
        summary_list = []
        for row in data:
            summary_list.append({
                "department": row.department,
                "jumlah_staff": row.jumlah_staff
            })
            
        return summary_list
    

    # ==========================================
    # UPDATE DEPARTMENTS
    # ==========================================
    def update_dept(self, id_dept: str, dept : DepartmentsUpdateSchema ) :

        dept_find = self.display_dept_by_uuid(id_dept)

        if not dept_find :
            raise HTTPException(
                404,
                "Department Tidak Ditemukan"
            )

        if self.repo.get_dept_by_dept(dept.name.upper()) :
            raise HTTPException(
                409,
                "Department Sudah Terdaftar"
            )


        dept_find.name = dept.name

        return self.repo.update_dept(dept_find)

    # ==========================================
    # DELETE DEPARTMENTS
    # ==========================================
    def delete_dept(self, id_dept: str) :

        dept_find = self.display_dept_by_uuid(id_dept)

        if not dept_find :
            raise HTTPException(
                404,
                "Department Tidak Ditemukan"
            )

        if dept_find.users:
            raise HTTPException(
                409,
                "Tidak dapat menghapus department karena masih ada user yang terkait"
            )

        if dept_find.history:
            raise HTTPException(
                409,
                "Tidak dapat menghapus department karena masih ada history yang terkait"
            )

        return self.repo.delete_dept(dept_find)