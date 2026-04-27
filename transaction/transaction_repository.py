from sqlalchemy.orm import Session
from models.models.models import HistoryUpload, StatusEnum

class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_paginated_transactions(self, model_class, skip: int, limit: int, user_id_filter: int = None):
        # 1. Join tabel Fact (contoh: FactFinance) dengan HistoryUpload
        query = self.db.query(model_class).join(
            HistoryUpload, model_class.id_history == HistoryUpload.id_history_upload
        )

        # 2. Jika ada nik_filter (berarti dia Staff), saring datanya
        if user_id_filter:
            query = query.filter(HistoryUpload.id_users == user_id_filter)

        # 3. Hitung total untuk pagination
        total_count = query.count()

        # 4. Ambil data dengan offset & limit
        results = query.order_by(model_class.id_fact.desc())\
                       .offset(skip)\
                       .limit(limit)\
                       .all()
                       
        return results, total_count

    def update_single_row(self, model_class, id_fact: int, new_value: float, manager_nik: str):
        # Cari data berdasarkan ID tabel fact yang dilempar
        row = self.db.query(model_class).get(id_fact)
        
        if not row:
            raise ValueError("Data tidak ditemukan di database.")
            
        # Pengecekan relasi ke History (harus PENDING)
        if row.history.status != StatusEnum.PENDING:
            raise ValueError("Hanya data berstatus PENDING yang bisa dikoreksi.")

        # # Logic Audit Trail
        # if not row.is_edited:
        #     row.original_value = row.value # Simpan data asli Excel
            
        row.value = new_value
        # row.is_edited = True
        # row.edited_by = manager_nik
        
        self.db.commit()
        return row
    