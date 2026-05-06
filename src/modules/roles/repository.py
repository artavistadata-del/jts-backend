from sqlalchemy.orm import Session
from src.models.models import Roles


class RoleRepository:
    def __init__(self, db : Session):
        self.db = db

    # ==========================================
    # GET ROLE BY ID [ADMIN ACCESS ]
    # ==========================================
    def get_role_by_id(self, id : int) :
        return self.db.query(Roles).filter(Roles.id == id).first()
    
    # ==========================================
    # GET ROLE BY UUID [ADMIN ACCESS ]
    # ==========================================
    def get_role_by_uuid(self, id : str) :
        return self.db.query(Roles).filter(Roles.public_id == id).first()
    
    # ==========================================
    # GET ROLE BY ROLE [ADMIN ACCESS]
    # ==========================================
    def get_role_by_role(self, role : str) :
        return self.db.query(Roles.id_roles).filter(Roles.name == role).first()
    
    # ==========================================
    # GET ALL ROLE [ADMIN ACCESS]
    # ==========================================
    def get_all_role(self) :
        return self.db.query(Roles).all()