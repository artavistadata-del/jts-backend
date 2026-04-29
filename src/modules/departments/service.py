from fastapi import HTTPException

from src.modules.departments.repository import DepartmentRepository
from src.models.models import Departments
from src.modules.departments.schema import DepartmentsInsertSchema


class DepartmentService :
    def __init__(self, dept_repo : DepartmentRepository):
        self.repo = dept_repo

    def display_dept_by_dept(self, name : str) :
        return self.repo.get_dept_by_dept(name)
    
    def display_dept_by_id(self, id_dept : id) :
        return self.repo.get_dept_by_id(id_dept)
    
    def display_all_dept(self) :
        dept_find = self.repo.get_all_dept()
        
        if not dept_find:
            raise HTTPException(404, "Belum Ada Department")
        
        hasil_format = []
        for r in dept_find:
            hasil_format.append({
                "id_dept": r.id_dept,
                "dept_name": r.name_dept
            })
        
        return {
            "message": "Berhasil mengambil data department",
            "data": hasil_format
        }
    

    def add_dept(self, dept : DepartmentsInsertSchema) :
        find_dept = self.display_dept_by_dept(dept.dept_name.upper())

        print(find_dept)

        if find_dept :
            raise HTTPException(302, " Department Sudah Ada")

        dept_model = Departments(
                name_dept = dept.dept_name
        )
        return self.repo.insert_dept(dept_model)


    def get_department_staff_summary(self):
        data = self.repo.get_staff_count_per_dept()
        
        summary_list = []
        for row in data:
            summary_list.append({
                "department": row.department,
                "jumlah_staff": row.jumlah_staff
            })
            
        return summary_list