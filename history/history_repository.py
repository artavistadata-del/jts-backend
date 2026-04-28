from sqlalchemy.orm import Session, defer
from models.models.models import HistoryUpload, RoleEnum, Users

class HistoryRepository :
    def __init__(self, db : Session):
        self.db = db

    def get_history_by_id_user(self, id_user : int) :
        self.db.query(HistoryUpload).filter(HistoryUpload.id_users == id_user)

    def get_history_by_id_hist(self, id_hist : int) :
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
    

    def get_history_by_access(self, id_users : int, role_name: str, id_dept: int, skip: int = 0, limit: int = 10):
        # # 1. Mulai dengan query dasar tanpa filter
        # query = self.db.query(HistoryUpload).options(
        #             defer(HistoryUpload.analysis_result),
        #             defer(HistoryUpload.file_name_storage)
        #         )

        query = self.db.query(
            HistoryUpload, 
            Users.nik, 
            Users.nama
        ).join(
            Users, HistoryUpload.id_users == Users.idusers
        ).options(
            defer(HistoryUpload.analysis_result),
            defer(HistoryUpload.file_name_storage)
        )
        
        # 2. Terapkan filter berdasarkan Role
        if role_name == RoleEnum.MANAGER or role_name == RoleEnum.DIREKTUR:
            # Manager/Direktur: Lihat semua data di departemennya
            query = query.filter(HistoryUpload.id_dept == id_dept)
                     
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
        
        # return results, total_count

        # 4. FORMAT ULANG DATA AGAR AMAN DI-JSON-KAN OLEH FASTAPI
        formatted_results = []
        for row in results:
            history_obj = row[0] # Objek HistoryUpload
            nik_user = row[1]    # Users.nik
            nama_user = row[2]   # Users.nama
            
            # Ekstrak manual ke dictionary bersih
            hist_dict = {
                "id_history_upload": history_obj.id_history_upload,
                "id_users": history_obj.id_users,
                "id_roles": history_obj.id_roles,
                "id_dept": history_obj.id_dept,
                "file_name": history_obj.file_name,
                "notes": history_obj.notes,
                "time_stamp": history_obj.time_stamp.isoformat() if history_obj.time_stamp else None,
                "status": history_obj.status.value if history_obj.status else None,
                "nik": nik_user,
                "nama_user": nama_user
            }
            formatted_results.append(hist_dict)
        
        # Return dictionary yang sudah bersih
        return formatted_results, total_count
    

    def delete_related_facts(self, model_class, id_history: int):
        """Menghapus semua baris transaksi di tabel fact yang terkait dengan history ini"""
        self.db.query(model_class).filter(model_class.id_history == id_history).delete()
        self.db.commit()
