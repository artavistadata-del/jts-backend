from src.models.models.models import Users
from sqlalchemy.orm import Session, joinedload


class UserRepository :
    def __init__(self, db : Session):
        self.db = db

    def insert_user(self, user : Users) :
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return "User Berhasil Ditambahkan"
    
    def get_user_by_nik(self, nik : str) :
        return self.db.query(Users).filter(Users.nik == nik).first()
    
    def get_user_by_id(self, id : int) :
        return self.db.query(Users).filter(Users.idusers == id).first()
    
    def get_all_user_paginated(self, skip: int, limit: int):
        total_data = self.db.query(Users).count()
        
        users = (
            self.db.query(Users)
            .options(
                joinedload(Users.roles),
                joinedload(Users.departments)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return total_data, users
    

    def deactivate_user(self, id_user : int):
        user = self.get_user_by_id(id_user)
        if user:
            user.is_active = False
            self.db.commit()
            return True
        return False
        

    # def hard_delete_user(self, nik: str):
    #     user = self.select_user(nik)
    #     if user:
    #         self.db.delete(user)
    #         self.db.commit()
    #         return True
    #     return False
    

    def update_user(self, user: Users):
        self.db.commit()
        self.db.refresh(user)
        return "Data User Berhasil Diperbarui"
    

    def reactivate_user(self, id_user : int):
        user = self.get_user_by_id(id_user)
        
        if user:
            user.is_active = True
            
            self.db.commit()
            return True
        return False
        
