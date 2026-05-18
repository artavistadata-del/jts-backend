import polars as pl
from sqlalchemy import text
from src.core.database import engine
from src.models.models import History, StatusEnum
from src.workers.cleaning.abstract_cleaning import AbstractCleaningService
from src.workers.cleanser.sales import process_sales_excel
from src.workers.queries.sales import SalesQueries
from src.workers.mappers.sales import SalesMapper

class SalesService(AbstractCleaningService):
    def __init__(self, db_session):
        super().__init__(db_session)
        self.id_dept = 2 
        self.stg_table = "stg_table.sales_transactions"

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
            df_excel = self._download_and_clean(history_id, filename, self.id_dept, process_sales_excel)
            
        
            df_height = df_excel.height

            # =========================================
            # Mapping
            # =========================================
            rule_stmt = SalesQueries.get_view_data("vw_all_masters")
            df_mapping = pl.read_database(query=rule_stmt, connection=engine)
            df_staging = SalesMapper.map_to_staging(df_excel, df_mapping, history_id)

            # =========================================
            # PUSH KE DATABASE
            # =========================================
            self._push_staging_to_db(df_staging, history_id, self.stg_table)


            record.status = StatusEnum.AWAITING_PREVIEW
            self.db.commit()

            return {
                "dept_name": "SALES",
                "sheet_processed": 1,
                "total_row_excel": df_height,
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
            
            self.db.execute(
                text(f"DELETE FROM {self.stg_table} WHERE history_id = :h_id"),
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
            self._move_staging_to_main(history_id, self.stg_table, "oltp_sales.transactions")
            
            record.status = StatusEnum.APPROVED
            
            self.db.execute(text(f"DELETE FROM {self.stg_table} WHERE history_id = :h_id"), {"h_id": history_id})

            self.db.commit()

            return {"status": "success", "message": "Data berhasil di-commit secara permanen."}

        except Exception as e:
            self.db.rollback()
            raise e
        
    # ==========================================
    # HELPER: PINDAHKAN STAGING KE MAIN (UPSERT)
    # ==========================================
    def _move_staging_to_main(self, history_id: int, stg_table: str, main_table: str):
        upsert_query = SalesQueries.insert_into_main(stg_table, main_table)
        self.db.execute(upsert_query, {"h_id": history_id})