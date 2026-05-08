from datetime import datetime

from src.models.models import Users
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session, joinedload


class UserRepository :
    def __init__(self, db : Session):
        self.db = db
    
    # ==========================================
    # INSERT USER
    # ==========================================
    def insert_user(self, user : Users) :
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return f"{user.name} Berhasil Ditambahkan"
    
    # ==========================================
    # GET USER BY NIK
    # ==========================================
    def get_user_by_nik(self, nik : str) :
        return self.db.query(Users).filter(
            Users.nik == nik,
            Users.deleted_at.is_(None)
            
            ).first()
    
    # ==========================================
    # GET USER BY UUID
    # ==========================================
    def get_user_by_uuid(self, public_id: str) -> Users:
        return self.db.query(Users).filter(
            Users.public_id == public_id, 
            Users.deleted_at.is_(None)
        ).first()
    
    # ==========================================
    # GET USER BY ID
    # ==========================================
    def get_user_by_id(self, id : int) :
        return self.db.query(Users).filter(
            Users.id == id, 
            Users.deleted_at.is_(None)
        ).first()
    
    # ==========================================
    # GET ALL USER [ ADMIN ACCESS ]
    # ==========================================
    # def get_all_user_paginated(self, skip: int, limit: int):
    #     total_data = self.db.query(Users).count()
        
    #     users = (
    #         self.db.query(Users)
    #         .options(
    #             joinedload(Users.role),
    #             joinedload(Users.department)
    #         )
    #         .offset(skip)
    #         .limit(limit)
    #         .all()
    #     )
        
    #     return total_data, users

    # sort by name
    def get_all_user_paginated(self, skip: int, limit: int, sort_by: str = "name", sort_order: str = "asc"):
        total_data = self.db.query(Users).filter(Users.deleted_at.is_(None)).count()
        
        sort_column = getattr(Users, sort_by, Users.name)
        
        if sort_order.lower() == "desc":
            order_expression = desc(sort_column)
        else:
            order_expression = asc(sort_column)
        
        users = (
            self.db.query(Users)
            .filter(Users.deleted_at.is_(None))
            .options(
                joinedload(Users.role),
                joinedload(Users.department)
            )
            .order_by(order_expression)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return total_data, users
    
    # ==========================================
    # DEACTIVE USER [ ADMIN ACCESS ]
    # ==========================================
    def deactivate_user(self, id_user : int):
        user = self.get_user_by_id(id_user)
        if user:
            user.is_active = False
            self.db.commit()
            return True
        return False
        
    # ==========================================
    # UPDATE USER [ ADMIN & USER ACCESS ]
    # ==========================================
    def update_user(self, user: Users):
        self.db.commit()
        self.db.refresh(user)
        return "Data User Berhasil Diperbarui"
    
    # ==========================================
    # REACTIVE USER [ ADMIN ACCESS ]
    # ==========================================
    def reactivate_user(self, id_user : int):
        user = self.get_user_by_id(id_user)
        
        if user:
            user.is_active = True
            
            self.db.commit()
            return True
        return False
    
    # ==========================================
    # DELETE USER [ ADMIN ACCESS ]
    # ==========================================
    def delete_user(self, id_user : int):
        user = self.get_user_by_id(id_user)
        
        if user:
            user.is_active = False
            user.deleted_at = datetime.now() 

            
            self.db.commit()
            return True
        return False
        
