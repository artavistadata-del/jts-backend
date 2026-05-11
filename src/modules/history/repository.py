from sqlalchemy.orm import Session, defer
from src.models.models import History, RoleEnum, Users

class HistoryRepository :
    def __init__(self, db : Session):
        self.db = db
    
    # ==========================================
    # GET HISTORY BY ID
    # ==========================================
    def get_history_by_id_hist(self, id_hist : int) :
        return self.db.query(History).filter(History.id == id_hist).first()
    
    # ==========================================
    # GET HISTORY BY UUID
    # ==========================================
    def get_history_by_uuid_hist(self, uuid_hist : str) :
        return self.db.query(History).filter(History.public_id == uuid_hist).first()

    # ==========================================
    # INSERT HISTORY -> Upload File [ USERS ACCESS ]
    # ==========================================
    def insert_history(self, history : History) :
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history
    
    # ==========================================
    # UPDATE HISTORY -> Approve/Reject [ ADMIN ACCESS ]
    # ==========================================
    def update_history(self, history: History):
        self.db.commit()
        self.db.refresh(history)
        return history
    
    # ==========================================
    # GET HISTORY ALL [ MANAGER & STAFF DEPT ACCESS ]
    # ==========================================
    def get_history_by_access(self, id_users : int, role_name: str, id_dept: int, skip: int = 0, limit: int = 10):
        query = self.db.query(
            History, 
            Users.nik, 
            Users.name
        ).join(
            Users, History.user_id == Users.id
        ).options(
            # defer(History.analysis_result),
            defer(History.file_name_storage)
        )
        
        # 2. Terapkan filter berdasarkan Role
        if role_name == RoleEnum.MANAGER or role_name == RoleEnum.DIREKTUR:
            # Manager/Direktur: Lihat semua data di departemennya
            query = query.filter(History.department_id == id_dept)
                     
        else:
            # Staff (Default): Hanya melihat transaksinya sendiri
            query = query.filter(History.user_id == id_users)

        # 3. Hitung total dan eksekusi pagination
        total_count = query.count()
        results = (
            query.order_by(History.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        # 4. FORMAT ULANG DATA AGAR AMAN DI-JSON-KAN OLEH FASTAPI
        formatted_results = []
        for row in results:
            history_obj = row[0] # Objek History
            nik_user = row[1]    # Users.nik
            nama_user = row[2]   # Users.nama
            
            # Ekstrak manual ke dictionary bersih
            hist_dict = {
                "id": history_obj.public_id,
                # "user_id": history_obj.user_id,
                # "role_id": history_obj.role_id,
                # "department_id": history_obj.department_id,
                "file_name": history_obj.file_name,
                "note": history_obj.note,
                "time_stamp": history_obj.time_stamp.isoformat() if history_obj.time_stamp else None,
                "status": history_obj.status.value if history_obj.status else None,
                "user" : {
                    "nik": nik_user,
                    "name": nama_user,
                },
                "analysis_result" : history_obj.analysis_result
            }
            formatted_results.append(hist_dict)
        
        # Return dictionary yang sudah bersih
        return formatted_results, total_count
    
    # ==========================================
    # DELETE HISTORY -> REJECT [ MANAGER ACCESS ]
    # ==========================================
    def delete_related_facts(self, model_class, id_history: int):
        """Menghapus semua baris transaksi di tabel fact yang terkait dengan history ini"""
        self.db.query(model_class).filter(model_class.id == id_history).delete()
        self.db.commit()
