from sqlalchemy.orm import Session, defer
from models.models.models import HistoryUpload, RoleEnum

class HistoryRepository :
    def __init__(self, db : Session):
        self.db = db

    def select_history_by_id_user(self, id_user : int) :
        self.db.query(HistoryUpload).filter(HistoryUpload.id_users == id_user)

    def select_history_by_id_hist(self, id_hist : int) :
        return self.db.query(HistoryUpload).filter(HistoryUpload.id_history_upload == id_hist).first()

    def insert_history(self, history : HistoryUpload) :
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history
    

    def update_history(self, history: HistoryUpload):
        self.db.commit()
        self.db.refresh(history)
        return history
    

    def select_history_by_access(self, id_users : int, role_name: str, id_dept: int, skip: int = 0, limit: int = 10):
        # 1. Mulai dengan query dasar tanpa filter
        query = self.db.query(HistoryUpload).options(defer(HistoryUpload.analysis_result))
        
        # 2. Terapkan filter berdasarkan Role
        if role_name == RoleEnum.MANAGER or role_name == RoleEnum.DIREKTUR:
            # Manager/Direktur: Lihat semua data di departemennya
            query = query.filter(HistoryUpload.id_dept == id_dept)
            
        elif role_name == RoleEnum.ADMIN:
            # Admin: Lihat seluruh data tanpa filter departemen (Opsional)
            pass 
            
        else:
            # Staff (Default): Hanya melihat transaksinya sendiri
            query = query.filter(HistoryUpload.id_users == id_users)

        # 3. Hitung total dan eksekusi pagination
        total_count = query.count()
        results = (
            query.order_by(HistoryUpload.id_history_upload.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return results, total_count
