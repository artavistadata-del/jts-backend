import io
from config.minio_conf import minio_client
from models.models.models import HistoryUpload, StatusEnum, FactFinance
from cleaners.finance_cleanser import process_finance_excel

class CleaningService:
    def __init__(self, db_session):
        self.db = db_session
        self.minio = minio_client

    def get_cleanser(self, id_dept: int):
        if id_dept == 1:
            return process_finance_excel
        else:
            raise ValueError(f"Belum ada cleanser untuk departemen {id_dept}")

    def run(self, history_id: int, filename: str, id_dept: int):
        record = self.db.query(HistoryUpload).filter(HistoryUpload.id_history_upload == history_id).first()
        record.status = StatusEnum.PENDING
        self.db.commit()

        try:
            raw_bucket = f"raw-dept-{id_dept}"
            
            response = self.minio.get_object(raw_bucket, filename)
            raw_bytes = io.BytesIO(response.read())
            response.close()
            response.release_conn()

            cleanser_func = self.get_cleanser(id_dept)
            
            df_dicts = cleanser_func(raw_bytes, history_id) 

            self.db.bulk_insert_mappings(FactFinance, df_dicts)

            record.status = StatusEnum.PENDING 
            record.is_synced = True
            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback() # Wajib rollback DB kalau insert gagal
            record.status = StatusEnum.REJECTED
            self.db.commit()
            raise e

# ==================================================
# Original tanpa insert data excel ke db
# ==================================================
    # def run(self, history_id: int, filename: str, id_dept: int):
    #     record = self.db.query(HistoryUpload).filter(HistoryUpload.id_history_upload == history_id).first()
    #     record.status = StatusEnum.PENDING
    #     self.db.commit()

    #     try:
    #         # 2. Ambil dari MinIO Raw
    #         raw_bucket = f"raw-dept-{id_dept}"
    #         clean_bucket = f"cleaned-dept-{id_dept}"
            
    #         response = self.minio.get_object(raw_bucket, filename)
    #         raw_bytes = io.BytesIO(response.read())
    #         response.close()
    #         response.release_conn()

    #         # 3. Panggil Logika Polars berdasarkan departemen
    #         cleanser_func = self.get_cleanser(id_dept)
    #         cleaned_bytes = cleanser_func(raw_bytes)
    #         # cleaned_bytes.seek(0)

    #         print(cleaned_bytes)

    #         # 5. Update status DB -> SUCCESS
    #         record.status = StatusEnum.APPROVED
    #         record.is_synced = True
    #         self.db.commit()
    #         return True

    #     except Exception as e:
    #         # 6. Jika gagal, catat FAILED
    #         record.status = StatusEnum.REJECTED
    #         self.db.commit()
    #         raise e


# # ======================================================================================
# # Insert untuk schema oltp
# #=========================================================================================

# import io
# import polars as pl
# from config.minio_conf import minio_client
# # Pastikan import semua model yang dibutuhkan
# from models.models.models import (
#     HistoryUpload, MasterSubSubCategory, StatusEnum, 
#     MasterCategory, MasterSubCategory, MasterAccount, 
#     DataSheet1, DataSheet2
# )
# from cleaners.finance_cleanser import process_finance_excel

# class CleaningService:

#     def __init__(self, db_session):
#         self.db = db_session
#         self.minio = minio_client

#     def get_cleanser(self, id_dept: int):
#         if id_dept == 1:
#             return process_finance_excel
#         else:
#             raise ValueError(f"Belum ada cleanser untuk departemen {id_dept}")

#     def _insert_to_db(self, history_id: int, df_bs: pl.DataFrame, df_is: pl.DataFrame):
#         """Memasukkan data Polars DataFrame ke dalam Database Relasional"""
        
#         # 1. Convert Polars DF ke List of Dictionaries
#         bs_data = df_bs.to_dicts()
#         is_data = df_is.to_dicts()

#         # 2. In-Memory Cache untuk Tabel Master
#         db_cats = {c.category_name: c.id_category for c in self.db.query(MasterCategory).all()}
#         db_subcats = {s.sub_category_name: s.id_sub_category for s in self.db.query(MasterSubCategory).all()}
#         # === CACHE UNTUK SUB SUB CATEGORY ===
#         db_subsubcats = {ss.sub_sub_category_name: ss.id_sub_sub_category for ss in self.db.query(MasterSubSubCategory).all()}
        
#         db_accs = {a.account_name: a.id_account for a in self.db.query(MasterAccount).all()}

#         # Helper functions untuk Get or Create Master Data
#         def get_cat_id(name, idx):
#             if not name: return None
#             if name not in db_cats:
#                 new_obj = MasterCategory(category_name=name, idx_category=str(idx) if idx is not None else None)
#                 self.db.add(new_obj)
#                 self.db.flush() 
#                 db_cats[name] = new_obj.id_category
#             return db_cats[name]

#         def get_subcat_id(cat_id, name, idx):
#             if not name: return None
#             if name not in db_subcats:
#                 new_obj = MasterSubCategory(id_category=cat_id, sub_category_name=name, idx_sub_category=str(idx) if idx is not None else None)
#                 self.db.add(new_obj)
#                 self.db.flush()
#                 db_subcats[name] = new_obj.id_sub_category
#             return db_subcats[name]
            
#         # === HELPER UNTUK SUB SUB CATEGORY ===
#         def get_subsubcat_id(subcat_id, name):
#             if not name: return None
#             if name not in db_subsubcats:
#                 new_obj = MasterSubSubCategory(id_sub_category=subcat_id, sub_sub_category_name=name)
#                 self.db.add(new_obj)
#                 self.db.flush()
#                 db_subsubcats[name] = new_obj.id_sub_sub_category
#             return db_subsubcats[name]

#         def get_acc_id(name):
#             if not name: return None
#             if name not in db_accs:
#                 new_obj = MasterAccount(account_name=name)
#                 self.db.add(new_obj)
#                 self.db.flush()
#                 db_accs[name] = new_obj.id_account
#             return db_accs[name]

#         # 3. Proses Insert Data Sheet 1 (BS)
#         bs_insert_list = []
#         for row in bs_data:
#             cat_id = get_cat_id(row.get('Category'), row.get('Idx Category'))
#             subcat_id = get_subcat_id(cat_id, row.get('Sub Category'), row.get('Idx Sub Category'))
#             # === DAPATKAN ID SUB SUB CATEGORY ===
#             subsubcat_id = get_subsubcat_id(subcat_id, row.get('Sub Sub Category'))
#             acc_id = get_acc_id(row.get('Account Name'))

#             bs_insert_list.append(
#                 DataSheet1(
#                     id_history_upload=history_id,
#                     id_category=cat_id,
#                     id_sub_category=subcat_id,
#                     id_sub_sub_category=subsubcat_id, # <--- UPDATE DISINI
#                     id_account=acc_id,
#                     bulan=row.get('Bulan'),
#                     value=row.get('Value')
#                 )
#             )

#         # 4. Proses Insert Data Sheet 2 (IS)
#         is_insert_list = []
#         for row in is_data:
#             cat_id = get_cat_id(row.get('Category'), None) 
#             subcat_id = get_subcat_id(cat_id, row.get('Sub Category'), row.get('Idx Sub Category'))
#             acc_id = get_acc_id(row.get('Account Name'))

#             is_insert_list.append(
#                 DataSheet2(
#                     id_history_upload=history_id,
#                     id_category=cat_id,
#                     id_sub_category=subcat_id,
#                     id_account=acc_id,
#                     bulan=row.get('Bulan'),
#                     value=row.get('Value')
#                 )
#             )

#         # 5. Eksekusi Bulk Insert Transaksi
#         self.db.add_all(bs_insert_list)
#         self.db.add_all(is_insert_list)
#         # 5. Eksekusi Bulk Insert Transaksi
#         self.db.add_all(bs_insert_list)
#         self.db.add_all(is_insert_list)
#         # Jangan dicommit dulu di sini, biarkan fungsi run() yang melakukan commit terakhir


#     def run(self, history_id: int, filename: str, id_dept: int):
#         # =================================================================
#         # 1. CEK DUPLIKASI DATA DI AWAL (OPSI 1: TOLAK JIKA SUDAH ADA)
#         # =================================================================
#         existing_upload = self.db.query(HistoryUpload).filter(
#             HistoryUpload.file_name == filename,
#             HistoryUpload.status == StatusEnum.APPROVED,
#             HistoryUpload.id_history_upload != history_id # Abaikan ID task yang sedang berjalan
#         ).first()

#         if existing_upload:
#             # Jika duplikat, langsung set task ini jadi REJECTED dan hentikan proses
#             record = self.db.query(HistoryUpload).filter(HistoryUpload.id_history_upload == history_id).first()
#             record.status = StatusEnum.REJECTED
#             self.db.commit()
#             raise ValueError(f"File '{filename}' sudah pernah diupload dan sukses diproses sebelumnya.")

#         # Jika lolos pengecekan, lanjut ambil record saat ini
#         record = self.db.query(HistoryUpload).filter(HistoryUpload.id_history_upload == history_id).first()
#         record.status = StatusEnum.PENDING
#         self.db.commit()

#         try:
#             # 2. Ambil dari MinIO Raw
#             raw_bucket = f"raw-dept-{id_dept}"
            
#             response = self.minio.get_object(raw_bucket, filename)
#             raw_bytes = io.BytesIO(response.read())
#             response.close()
#             response.release_conn()

#             # 3. Panggil Logika Polars berdasarkan departemen
#             cleanser_func = self.get_cleanser(id_dept)
            
#             # Unpack tuple hasil Polars (df_bs_clean, df_is_clean)
#             df_bs, df_is = cleanser_func(raw_bytes) 

#             # 4. INSERT KE DATABASE
#             self._insert_to_db(history_id, df_bs, df_is)

#             # 5. Update status DB -> APPROVED
#             record.status = StatusEnum.APPROVED
#             record.is_synced = True
            
#             # Commit semua perubahan (termasuk insert dari _insert_to_db)
#             self.db.commit()
#             return True

#         except Exception as e:
#             # 6. Jika gagal, catat REJECTED dan Rollback
#             self.db.rollback() # Rollback jika gagal di tengah jalan
#             record.status = StatusEnum.REJECTED
#             self.db.commit()
#             raise e 