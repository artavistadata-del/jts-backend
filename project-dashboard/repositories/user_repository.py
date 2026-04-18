from models.models import User
from models.schemas import User as userData
from sqlalchemy.orm import Session


class UserRepository :
    def __init__(self, db : Session):
        self.db = db

    def insert_user(self, user : User) :
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def select_user(self, nik : str) :
        return self.db.query(User).filter(User.nik == nik).first()
        
