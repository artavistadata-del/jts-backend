import polars as pl
from sqlalchemy import text
from src.core.database import engine
from src.models.models import History, StatusEnum
from src.workers.cleaning.abstract_cleaning import AbstractCleaningService
from src.workers.cleanser.finance import process_finance_excel
from src.workers.queries.finance import FinanceQueries
from src.workers.mappers.finance import FinanceMapper

class FinanceService(AbstractCleaningService):
    def __init__(self, db_session):
        super().__init__(db_session)
        self.department_name = 'FINANCE'
        self.main_table = "oltp_finance.transactions"
        self.stg_table = "stg_table.finance_transactions"
        self.rule_lookup_view = "oltp_finance.vw_transaction_rule_lookup"
        self.join_cols = [
            "sheet_name", "category_name", "sub_category_name", 
            "sub_sub_category_name", "account_name", "actual_budget"
        ]

    # ==========================================
    # 1. TAHAP ANALYZE
    # ==========================================
    def execute_analyze(self, history_id: int, filename: str) -> dict:
        record = self.db.query(History).filter(History.id == history_id).first()
        if not record:
            raise ValueError(f"Data History dengan ID {history_id} tidak ditemukan.")

        try:
            # 1. Extract & Clean Data Mentah
            df_excel = self._download_and_clean(history_id, filename, self.department_name, process_finance_excel)
            total_row_excel = df_excel.height

            # 2. Get Rules dari Database & Siapkan Mapper
            rule_query = FinanceQueries.get_rule_lookup(self.rule_lookup_view)
            df_rule_raw = pl.read_database(query=rule_query, connection=engine)
            df_rule_clean = FinanceMapper.prepare_rule_lookup(df_rule_raw, self.join_cols)

            # 3. Transform / Mapping Data
            df_staging = FinanceMapper.map_to_staging(df_excel, df_rule_clean, self.join_cols, history_id)

            # 4. Load ke Staging Table
            self._push_staging_to_db(df_staging, history_id, self.stg_table)

            # =================================================================
            # TAMBAHKAN LANGKAH INI (4.5) UNTUK MENG-UPDATE KOLOM STATUS
            # =================================================================
            update_status_query = FinanceQueries.update_staging_status(self.stg_table, self.main_table)
            self.db.execute(update_status_query, {"history_id": history_id})
            self.db.commit() # Wajib commit agar statusnya tersimpan sebelum dibaca preview
            # =================================================================

            # 5. Hitung Preview & Warning (Khusus Finance)
            total_insert, preview_insert = self._get_preview_data(history_id, FinanceQueries.get_preview_insert)
            total_replace, preview_replace = self._get_preview_data(history_id, FinanceQueries.get_preview_replace)
            total_unchanged = total_row_excel - (total_insert + total_replace)
            warnings = self._detect_wip_mismatch(history_id)

            # 6. Sukses -> Simpan Analysis Result & Ubah Status
            record.analysis_result = {
                "dept_name": "FINANCE",
                "total_row_excel": total_row_excel,
                "total_insert": total_insert,
                "total_replace": total_replace,
                "total_unchanged": total_unchanged,
                "preview_insert": preview_insert,
                "preview_replace": preview_replace,
                "warnings": warnings,
                "status": "Sukses Diproses"
            }
            record.status = StatusEnum.AWAITING_PREVIEW
            self.db.commit()

            return record.analysis_result

        except Exception as e:
            self.db.rollback() 
            record.status = StatusEnum.FAILED
            record.analysis_result = {"error": str(e)}
            self.db.commit()
            raise e

    # ==========================================
    # 2. TAHAP COMMIT (UPSERT)
    # ==========================================
    def execute_commit(self, history_id: int, filename: str) -> dict:
        record = self.db.query(History).filter(History.id == history_id).first()
        valid_statuses = [StatusEnum.AWAITING_PREVIEW, StatusEnum.PROCESSING_INSERT]
        
        if not record or record.status not in valid_statuses:
            current_status = record.status.name if record else "Data Tidak Ditemukan"
            raise ValueError(f"Gagal Commit! Status tidak diizinkan. Status saat ini: {current_status}")

        try:
            upsert_query = FinanceQueries.insert_into_main(self.stg_table, self.main_table)
            self.db.execute(upsert_query, {"history_id": history_id})
            
            record.status = StatusEnum.APPROVED
            
            self.db.execute(text(f"DELETE FROM {self.stg_table} WHERE history_id = :h_id"), {"h_id": history_id})

            self.db.commit()
            return {"status": "success", "message": "Data berhasil di-commit secara permanen."}

        except Exception as e:
            self.db.rollback()
            record.status = StatusEnum.FAILED
            self.db.commit()
            raise e

    # ==========================================
    # 3. TAHAP CANCEL
    # ==========================================
    def execute_cancel(self, history_id: int, filename: str) -> dict:
        record = self.db.query(History).filter(History.id == history_id).first()
        if not record:
            raise ValueError("Data History tidak ditemukan.")

        try:
            self.db.execute(text(f"DELETE FROM {self.stg_table} WHERE history_id = :h_id"), {"h_id": history_id})
            record.status = StatusEnum.CANCELLED
            self.db.commit()
            return {"status": "success", "message": "Proses dibatalkan. Data staging telah dibersihkan."}

        except Exception as e:
            self.db.rollback()
            raise e

    # ==========================================
    # HELPER FUNCTIONS
    # ==========================================
    def _push_staging_to_db(self, df_staging: pl.DataFrame, history_id: int, table_name: str):
        self.db.execute(text(f"DELETE FROM {table_name} WHERE history_id = :h_id"), {"h_id": history_id})
        self.db.commit()
        db_uri = f"postgresql://{engine.url.username}:{engine.url.password}@{engine.url.host}:{engine.url.port}/{engine.url.database}"
        df_staging.write_database(table_name=table_name, connection=db_uri, if_table_exists="append", engine="sqlalchemy")

    def _get_preview_data(self, history_id: int, query_func):
        """Helper untuk mengeksekusi kueri preview (Insert/Replace) dan mengembalikan total & JSON preview"""
        query = query_func(self.stg_table, self.main_table)
        df_preview = pl.read_database(query=query, connection=engine, execute_options={"parameters": {"history_id": history_id}})
        return df_preview.height, df_preview.head(10).cast(pl.String).to_dicts()

    def _detect_wip_mismatch(self, history_id: int) -> list:
        """Mengeksekusi query peringatan WIP"""
        query = FinanceQueries.get_wip_mismatch(self.stg_table, self.main_table, self.rule_lookup_view)
        rows = self.db.execute(query, {"history_id": history_id}).fetchall()
        warnings = []
        for row in rows:
            val_beg = f"{row.nilai_beginning_baru:,.2f}" if row.nilai_beginning_baru is not None else "0"
            if row.nilai_ending_lama is None:
                warnings.append(f"⚠️ {row.bulan_upload}: Data WIP Ending Actual bulan lalu tidak ditemukan.")
            else:
                val_end = f"{row.nilai_ending_lama:,.2f}"
                warnings.append(f"⚠️ {row.bulan_upload}: WIP Beginning Actual ({val_beg}) ≠ WIP Ending bulan lalu ({val_end}).")
        return warnings