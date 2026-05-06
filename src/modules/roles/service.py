from src.modules.roles.repository import RoleRepository
from fastapi import HTTPException


class RoleService :
    def __init__(self, repo : RoleRepository):
        self.repo = repo
    # ==========================================
    # GET ROLE BY ROLE [ADMIN ACCESS]
    # ==========================================
    def display_role_by_role(self, role : str) :
        return self.repo.get_role_by_role(role)
    
    # ==========================================
    # GET ROLE BY ID [ADMIN ACCESS]
    # ==========================================
    def display_role_by_id(self, role : int) :
        return self.repo.get_role_by_id(role)
    
    # ==========================================
    # GET ROLE BY UUID [ADMIN ACCESS]
    # ==========================================
    def display_role_by_uuid(self, role : int) :
        return self.repo.get_role_by_uuid(role)

    # ==========================================
    # GET ALL ROLES [ADMIN ACCESS]
    # ==========================================
    def display_all_role(self):
        roles_find = self.repo.get_all_role()
        
        if not roles_find:
            raise HTTPException(404, "Belum Ada Role")
        
        hasil_format = []
        for r in roles_find:
            hasil_format.append({
                "id": r.public_id,
                "name": r.name
            })
        
        return {
            "message": "Berhasil mengambil data role",
            "data": hasil_format
        }