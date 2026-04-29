from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.models.models import Departments, Users


class DepartmentRepository :
    def __init__(self, db : Session):
        self.db = db

    def get_dept_by_dept(self, dept_name : str) :
        return self.db.query(Departments.id_dept).filter(Departments.name_dept == dept_name).first()
    
    def get_dept_by_id(self, dept_id : int) :
        return self.db.query(Departments.name_dept).filter(Departments.id_dept == dept_id).first()

    def get_all_dept(self) :
        return self.db.query(Departments).all()
    

    def insert_dept(self, dept : Departments) :
        self.db.add(dept)
        self.db.commit()
        self.db.refresh(dept)

        return "Berhasil"
    

    def get_staff_count_per_dept(self):
        results = (
            self.db.query(
                Departments.name_dept.label("department"),
                func.count(Users.idusers).label("jumlah_staff")
            )
            .outerjoin(Users, Departments.id_dept == Users.id_dept)
            .group_by(Departments.id_dept, Departments.name_dept)
            .order_by(Departments.name_dept.asc())
            .all()
        )
        return results
    