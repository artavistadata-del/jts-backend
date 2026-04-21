from sqlalchemy.orm import Session

from models.models.models import Departments


class DepartmentRepository :
    def __init__(self, db : Session):
        self.db = db

    def select_dept_by_dept(self, dept_name : str) :
        return self.db.query(Departments.id_dept).filter(Departments.name_dept == dept_name).first()
    
    def select_dept_by_id(self, dept_id : int) :
        return self.db.query(Departments.id_dept).filter(Departments.id_dept == dept_id).first()

    def select_all_dept(self) :
        return self.db.query(Departments).all()
    