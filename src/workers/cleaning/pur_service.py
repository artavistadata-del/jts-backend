import polars as pl
from sqlalchemy import text
from src.core.database import engine
from src.models.models import History, StatusEnum
from src.workers.cleaning.abstract_cleaning import AbstractCleaningService
from src.workers.cleanser.purchase import process_purchasing_excel
from src.workers.queries.purchasing import PurchasingQueries
from src.workers.mappers.purchasing_mapper import PurchasingMapper

class PurchaseService(AbstractCleaningService):
    def __init__(self, db_session):
        super().__init__(db_session)
        self.id_dept = 3 
        self.stg_table_sheet3 = "stg_table.purchasing_sheet3_transactions"
        self.stg_table_sheet2 = "stg_table.purchasing_sheet2_transactions"
        self.stg_table_sheet1 = "stg_table.purchasing_sheet1_transactions"

    # ==========================================
    # HUKUM WAJIB: ALUR KERJA UTAMA
    # ==========================================
    def execute_analyze(self, history_id: int, filename: str) -> dict:
        # 1. CARI DATA HISTORY DI DATABASE
        record = self.db.query(History).filter(History.id == history_id).first()
        if not record:
            raise ValueError(f"Data History dengan ID {history_id} tidak ditemukan.")

        try:
            # --- MULAI PROSES ETL ---
            df_excel = self._download_and_clean(history_id, filename, self.id_dept, process_purchasing_excel)
            
            total_row_excel = (
                df_excel["sheet1"].height + 
                df_excel["sheet2"].height + 
                df_excel["sheet3"].height
            )

            # =========================================
            # Mapping Sheet 3
            # =========================================
            rule_stmt = PurchasingQueries.get_view_data("vw_sheet3_rules")
            df_mapping_sheet3 = pl.read_database(query=rule_stmt, connection=engine)
            df_staging_sheet3 = PurchasingMapper.map_sheet3_to_staging(df_excel["sheet3"], df_mapping_sheet3, history_id)

            # =========================================
            # Mapping Sheet 2
            # =========================================
            rule_stmt = PurchasingQueries.get_view_data("vw_sheet2_master")
            df_mapping_sheet2 = pl.read_database(query=rule_stmt, connection=engine)
            df_staging_sheet2 = PurchasingMapper.map_sheet2_to_staging(df_excel["sheet2"], df_mapping_sheet2, history_id)

            # =========================================
            # Mapping Sheet 1 (Langsung jika tidak ada mapping khusus)
            # =========================================
            df_staging_sheet1 = df_excel["sheet1"]

            # =========================================
            # PUSH KE DATABASE
            # =========================================
            self._push_staging_to_db(df_staging_sheet3, history_id, self.stg_table_sheet3)
            self._push_staging_to_db(df_staging_sheet2, history_id, self.stg_table_sheet2)
            self._push_staging_to_db(df_staging_sheet1, history_id, self.stg_table_sheet1)

            record.status = StatusEnum.AWAITING_PREVIEW
            self.db.commit()

            return {
                "dept_name": "PURCHASING",
                "sheet_processed": 3,
                "total_row_excel": total_row_excel,
                "status": "Sukses Diproses"
            }

        except Exception as e:
            # 3. JIKA GAGAL: Batalkan transaksi staging, lalu ubah status history jadi FAILED
            self.db.rollback() 
            record.status = StatusEnum.FAILED
            self.db.commit()
            
            # (Opsional) Jika di model History Anda punya kolom untuk mencatat error, bisa pakai ini:
            # record.error_message = str(e)
            
            raise e # Lemparkan error kembali agar tercatat di log Celery

    # ==========================================
    # HELPER LOAD DATA (PUSH)
    # ==========================================
    def _push_staging_to_db(self, df_staging: pl.DataFrame, history_id: int, table_name: str):
        """Menyimpan data staging dengan aman ke target tabel yang spesifik"""
        
        delete_query = text(f"DELETE FROM {table_name} WHERE history_id = :h_id")
        self.db.execute(delete_query, {"h_id": history_id})
        self.db.commit()
        
        db_uri = f"postgresql://{engine.url.username}:{engine.url.password}@{engine.url.host}:{engine.url.port}/{engine.url.database}"
        
        df_staging.write_database(
            table_name=table_name, 
            connection=db_uri, 
            if_table_exists="append", 
            engine="sqlalchemy" # Ubah ke 'adbc' jika Anda sudah install adbc-driver-postgresql
        )

    # ==========================================
    # EKSEKUSI CANCEL (BATAL)
    # ==========================================
    def execute_cancel(self, history_id: int, filename: str) -> dict:
        """Membatalkan proses: Hapus data dari staging dan update status."""
        record = self.db.query(History).filter(History.id == history_id).first()
        if not record:
            raise ValueError("Data History tidak ditemukan.")

        try:
            for stg_table in [self.stg_table_sheet1, self.stg_table_sheet2, self.stg_table_sheet3]:
                self.db.execute(
                    text(f"DELETE FROM {stg_table} WHERE history_id = :h_id"),
                    {"h_id": history_id}
                )

            record.status = StatusEnum.CANCELLED
            self.db.commit()

            return {"status": "success", "message": "Proses dibatalkan. Data staging telah dibersihkan."}

        except Exception as e:
            self.db.rollback()
            raise e

    # ==========================================
    # EKSEKUSI COMMIT (SETUJUI)
    # ==========================================
    def execute_commit(self, history_id: int, filename: str) -> dict:
        """Menyetujui proses: Pindahkan data ke tabel utama dan update status."""
        record = self.db.query(History).filter(History.id == history_id).first()

        if not record or record.status != StatusEnum.PROCESSING_INSERT:
            raise ValueError(f"Data tidak valid atau belum dalam status AWAITING_PREVIEW{record.status}.")

        try:
            # PENTING: Pastikan nama tabel utama di sini sama persis dengan yang ada di database Anda
            self._move_staging_to_main_sheet3(history_id, self.stg_table_sheet3, "oltp_purchasing.sheet3_transactions")
            self._move_staging_to_main_sheet2(history_id, self.stg_table_sheet2, "oltp_purchasing.sheet2_transactions")
            self._move_staging_to_main_sheet1(history_id, self.stg_table_sheet1, "oltp_purchasing.sheet1_transactions")
            
            record.status = StatusEnum.APPROVED
            
            for stg_table in [self.stg_table_sheet1, self.stg_table_sheet2, self.stg_table_sheet3]:
                self.db.execute(text(f"DELETE FROM {stg_table} WHERE history_id = :h_id"), {"h_id": history_id})

            self.db.commit()

            return {"status": "success", "message": "Data berhasil di-commit secara permanen."}

        except Exception as e:
            self.db.rollback()
            raise e
        
    # ==========================================
    # HELPER: PINDAHKAN STAGING KE MAIN (UPSERT)
    # ==========================================
    def _move_staging_to_main_sheet3(self, history_id: int, stg_table: str, main_table: str):
        upsert_query = PurchasingQueries.insert_into_main_sheet3(stg_table, main_table)
        self.db.execute(upsert_query, {"h_id": history_id})

    def _move_staging_to_main_sheet2(self, history_id: int, stg_table: str, main_table: str):
        upsert_query = PurchasingQueries.insert_into_main_sheet2(stg_table, main_table)
        self.db.execute(upsert_query, {"h_id": history_id})

    def _move_staging_to_main_sheet1(self, history_id: int, stg_table: str, main_table: str):
        upsert_query = PurchasingQueries.insert_into_main_sheet1(stg_table, main_table)
        self.db.execute(upsert_query, {"h_id": history_id})