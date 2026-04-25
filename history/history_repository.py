from sqlalchemy.orm import Session, defer
from models.models.models import HistoryUpload

class HistoryRepository :
    def __init__(self, db : Session):
        self.db = db

    def select_history_by_nik(self, nik : str) :
        self.db.query(HistoryUpload).filter(HistoryUpload.users_nik == nik)

    def select_history_by_id_hist(self, id_hist : int) :
        return self.db.query(HistoryUpload).filter(HistoryUpload.id_history_upload == id_hist).first()

    def insert_history(self, history : HistoryUpload) :
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history
    
    def select_history_by_nik(self, nik: str, skip: int = 0, limit: int = 10):
        query = self.db.query(HistoryUpload)\
                    .filter(HistoryUpload.users_nik == nik)\
                    .options(defer(HistoryUpload.analysis_result))        
        total_count = query.count()
        
        results = query.order_by(HistoryUpload.id_history_upload.desc())\
                       .offset(skip)\
                       .limit(limit)\
                       .all()
        return results, total_count
    
    def update_history(self, history: HistoryUpload):
        self.db.commit()
        self.db.refresh(history)
        return history
