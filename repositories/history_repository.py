from sqlalchemy.orm import Session
from models.models import HistoryUpload

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