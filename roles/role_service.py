from roles.role_repository import RoleRepository
from fastapi import HTTPException


class RoleService :
    def __init__(self, repo : RoleRepository):
        self.repo = repo

    def display_role_by_role(self, role : str) :
        return self.repo.select_role_by_role(role)
    

    def display_all_role(self):
        roles_find = self.repo.select_all_role()
        
        if not roles_find:
            raise HTTPException(404, "Belum Ada Role")
        
        hasil_format = []
        for r in roles_find:
            hasil_format.append({
                "id_roles": r.id_roles,
                "role_name": r.role
            })
        
        return {
            "message": "Berhasil mengambil data role",
            "data": hasil_format
        }