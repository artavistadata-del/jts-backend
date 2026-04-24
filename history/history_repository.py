from sqlalchemy.orm import Session, defer
from models.models.models import HistoryUpload

class HistoryRepository :
    def __init__(self, db : Session):
        self.db = db

    def select_history_by_nik(self, nik : str) :
        self.db.query(HistoryUpload).filter(HistoryUpload.users_nik == nik)

    def insert_history(self, history : HistoryUpload) :
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history
    
    def select_history_by_nik(self, nik: str, skip: int = 0, limit: int = 10):
# Gunakan .defer() untuk mengabaikan kolom analysis_result saat query
        query = self.db.query(HistoryUpload)\
                    .filter(HistoryUpload.users_nik == nik)\
                    .options(defer(HistoryUpload.analysis_result))        
        # Menghitung total data untuk keperluan metadata pagination di frontend
        total_count = query.count()
        
        # Mengambil data dengan limit dan offset
        results = query.order_by(HistoryUpload.id_history_upload.desc())\
                       .offset(skip)\
                       .limit(limit)\
                       .all()
        return results, total_count
