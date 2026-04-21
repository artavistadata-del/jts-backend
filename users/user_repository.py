from models.models.models import Users
from sqlalchemy.orm import Session


class UserRepository :
    def __init__(self, db : Session):
        self.db = db

    def insert_user(self, user : Users) :
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return "User Berhasil Ditambahkan"
    
    def select_user(self, nik : str) :
        return self.db.query(Users).filter(Users.nik == nik).first()
        
