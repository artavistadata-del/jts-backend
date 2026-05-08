from sqlalchemy import desc, func, asc
from sqlalchemy.orm import Session
from src.models.models import Departments, Users


class DepartmentRepository :
    def __init__(self, db : Session):
        self.db = db

    
    # ==========================================
    # GET DEPT BY DEPT [ADMIN ACCESS ]
    # ==========================================
    def get_dept_by_dept(self, dept_name : str) :
        return self.db.query(Departments.id).filter(Departments.name == dept_name).first()
    
    # ==========================================
    # GET DEPT BY ID [ADMIN ACCESS ]
    # ==========================================
    def get_dept_by_id(self, dept_id : int) :
        return self.db.query(Departments.name).filter(Departments.id == dept_id).first()
    
    # ==========================================
    # GET DEPT BY UUID [ADMIN ACCESS ]
    # ==========================================
    def get_dept_by_uuid(self, public_id : str) :
        return self.db.query(Departments).filter(Departments.public_id == public_id).first()
    
    # ==========================================
    # GET ALL DEPT [ADMIN ACCESS ]
    # ==========================================
    def get_all_dept(self, sort_by: str = "name", sort_order: str = "asc"):
        sort_column = getattr(Departments, sort_by, Departments.name)
        
        if sort_order.lower() == "desc":
            order_expression = desc(sort_column)
        else:
            order_expression = asc(sort_column)
            
        return self.db.query(Departments).order_by(order_expression).all()
    
    # ==========================================
    # INSERT DEPT [ADMIN ACCESS ]
    # ==========================================
    def insert_dept(self, dept : Departments) :
        self.db.add(dept)
        self.db.commit()
        self.db.refresh(dept)

        return "Berhasil"
    
    # ==========================================
    # GET DEPT WITH SUMMARY [ADMIN ACCESS ]
    # ==========================================
    def get_staff_count_per_dept(self):
        results = (
            self.db.query(
                Departments.name.label("department"),
                func.count(Users.id).label("jumlah_staff")
            )
            .outerjoin(Users, Departments.id == Users.department_id)
            .group_by(Departments.id, Departments.name)
            .order_by(Departments.name.asc())
            .all()
        )
        return results


    # ==========================================
    # UPDATE DEPARTMENTS
    # ==========================================
    def update_dept(self, dept : Departments) :

        self.db.commit()
        self.db.refresh(dept)
        return f"Data Department {dept.name} Berhasil Diperbarui"

    # ==========================================
    # DELETE DEPARTMENTS
    # ==========================================
    def delete_dept(self, dept : Departments) :

        self.db.delete(dept)
        self.db.commit()
        return f"Data Department {dept.name} Berhasil Dihapus"