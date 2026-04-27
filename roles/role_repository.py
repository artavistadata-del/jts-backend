from sqlalchemy.orm import Session
from models.models.models import Roles


class RoleRepository:
    def __init__(self, db : Session):
        self.db = db

    def get_role_by_id(self, id : int) :
        return self.db.query(Roles).filter(Roles.id_roles == id).first()
    
    def get_role_by_role(self, role : str) :
        return self.db.query(Roles.id_roles).filter(Roles.role == role).first()
    
    def get_all_role(self) :
        return self.db.query(Roles).all()