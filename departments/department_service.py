from fastapi import HTTPException

from departments.department_repository import DepartmentRepository


class DepartmentService :
    def __init__(self, dept_repo : DepartmentRepository):
        self.repo = dept_repo

    def display_dept_by_dept(self, name : str) :
        return self.repo.select_dept_by_dept(name)
    
    def display_dept_by_id(self, id_dept : id) :
        return self.repo.select_dept_by_id(id_dept)
    
    def display_all_dept(self) :
        dept_find = self.repo.select_all_dept()
        
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