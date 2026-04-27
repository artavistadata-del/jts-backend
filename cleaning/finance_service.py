import polars as pl
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import text
from cleaning.base_cleaning_service import BaseCleaningService
from cleaners.finance_cleanser import process_finance_excel
from config.config import engine 
from config.dept_registry import get_dept_config
from models.models.models import HistoryUpload, StatusEnum, FactFinance

class FinanceService(BaseCleaningService):
    def __init__(self, db_session):
        super().__init__(db_session)
        self.id_dept = 1
        self.unique_keys = [
            "bulan", "account_name", "report_type", 
            "idx_category", "category", "idx_sub_category", 
            "sub_category", "sub_sub_category"
        ]


    # ======================================================================
    # PYTHON COMPARE
    # ======================================================================
    # def execute_analyze(self, history_id: int, filename: str):
    #     df_excel = self._download_and_clean(history_id, filename, self.id_dept, process_finance_excel)
        
    #     query = """
    #         SELECT bulan, account_name, report_type, idx_category, category, 
    #                idx_sub_category, sub_category, sub_sub_category, value 
    #         FROM oltp_tes.fact_finance
    #     """

    #     df_db = pl.read_database(query=query, connection=engine)

    #     df_db = df_db.with_columns([
    #         pl.col("bulan").cast(pl.Date), pl.col("value").cast(pl.Float64),
    #         pl.col("account_name").cast(pl.String), pl.col("report_type").cast(pl.String),
    #         pl.col("idx_category").cast(pl.String), pl.col("category").cast(pl.String),
    #         pl.col("idx_sub_category").cast(pl.String), pl.col("sub_category").cast(pl.String),
    #         pl.col("sub_sub_category").cast(pl.String)
    #     ])

    #     string_keys = self.unique_keys[1:] 
    #     df_excel = df_excel.with_columns([pl.col(c).fill_null("") for c in string_keys])
    #     df_db = df_db.with_columns([pl.col(c).fill_null("") for c in string_keys])

    #     df_compare = df_excel.join(df_db, on=self.unique_keys, how="left", suffix="_db")
        
    #     df_insert = df_compare.filter(pl.col("value_db").is_null())
    #     total_insert = df_insert.height

    #     df_replace = df_compare.filter(
    #         (pl.col("value_db").is_not_null()) & 
    #         (pl.col("value") != pl.col("value_db"))
    #     )
    #     total_replace = df_replace.height

    #     total_unchanged = df_compare.filter(
    #         (pl.col("value_db").is_not_null()) & 
    #         (pl.col("value") == pl.col("value_db"))
    #     ).height

    #     # ==========================================
    #     # SIAPKAN PREVIEW DATA (Max 10 Baris)
    #     # ==========================================
    #     original_cols = df_excel.columns
        
    #     preview_insert = (
    #         df_insert.select(original_cols)
    #         .head(10)
    #         .cast(pl.String)
    #         .to_dicts()
    #     )
        
    #     preview_replace = (
    #         df_replace.select(original_cols)
    #         .head(10)
    #         .cast(pl.String)
    #         .to_dicts()
    #     )

    #     # 4. Simpan Hasil ke History Upload
    #     record = self.db.query(HistoryUpload).filter(HistoryUpload.id_history_upload == history_id).first()
    #     record.analysis_result = {
    #         "dept_name": "FINANCE",
    #         "total_insert": total_insert,
    #         "total_replace": total_replace,
    #         "total_unchanged": total_unchanged,
    #         "total_row_excel": df_excel.height,
    #         "preview_insert": preview_insert,
    #         "preview_replace": preview_replace 
    #     }
    #     record.status = StatusEnum.AWAITING_PREVIEW
    #     self.db.commit()

    # ===========================================================================================
    # POSTGRES COMPARE
    # ===========================================================================================
    def execute_analyze(self, history_id: int, filename: str):
        # 1. Bersihkan Data Excel seperti biasa
        df_excel = self._download_and_clean(history_id, filename, self.id_dept, process_finance_excel)
        
        # Isi null values agar SQL tidak bingung saat JOIN
        string_keys = self.unique_keys[1:] 
        df_excel = df_excel.with_columns([pl.col(c).fill_null("") for c in string_keys])
        total_row_excel = df_excel.height

        # 2. PUSH KE STAGING TABLE (Sangat Cepat & Aman untuk RAM)
        # Bikin nama tabel unik berdasarkan history_id agar tidak bentrok jika upload barengan
        stg_table = f"stg_finance_upload_{history_id}"
        
        # Gunakan string URI untuk Polars write_database
        db_uri = f"postgresql://{engine.url.username}:{engine.url.password}@{engine.url.host}:{engine.url.port}/{engine.url.database}"
        df_excel.write_database(
            table_name=stg_table, 
            connection=db_uri, 
            if_table_exists="replace",
            engine="adbc"
        )

        # 3. SUSUN KONDISI JOIN SECARA OTOMATIS
        # Menghasilkan: s.bulan = f.bulan AND s.account_name = f.account_name ... dsb
        join_conditions = " AND ".join([f"s.{key} = f.{key}" for key in self.unique_keys])

        try:
            # ==========================================
            # A. HITUNG & AMBIL PREVIEW INSERT (Data Baru)
            # ==========================================
            query_insert = text(f"""
                SELECT s.* FROM {stg_table} s
                LEFT JOIN oltp_tes.fact_finance f ON {join_conditions}
                WHERE f.bulan IS NULL
            """)
            
            # Tarik hasilnya ke Polars (hanya baris insert, bukan seluruh tabel fact!)
            df_insert = pl.read_database(query=query_insert, connection=engine)
            total_insert = df_insert.height
            preview_insert = df_insert.head(10).cast(pl.String).to_dicts()

            # ==========================================
            # B. HITUNG & AMBIL PREVIEW REPLACE (Data Beda Value)
            # ==========================================
            query_replace = text(f"""
                SELECT s.* FROM {stg_table} s
                JOIN oltp_tes.fact_finance f ON {join_conditions}
                WHERE s.value != f.value
            """)
            
            df_replace = pl.read_database(query=query_replace, connection=engine)
            total_replace = df_replace.height
            preview_replace = df_replace.head(10).cast(pl.String).to_dicts()

            # Hitung total unchanged
            total_unchanged = total_row_excel - (total_insert + total_replace)

        # finally:
        #     # 4. WAJIB: HAPUS STAGING TABLE SETELAH SELESAI
        #     # Pakai blok finally agar tabel tetap terhapus meskipun ada error
        #     self.db.execute(text(f"DROP TABLE IF EXISTS {stg_table}"))
        #     self.db.commit()

        except Exception as e:
            self.db.rollback()
            # Jika gagal, staging jangan dihapus dulu supaya bisa di-retry
            record.status = StatusEnum.FAILED
            self.db.commit()
            raise e

        # 5. SIMPAN HASIL KE HISTORY UPLOAD
        record = self.db.query(HistoryUpload).filter(HistoryUpload.id_history_upload == history_id).first()
        record.analysis_result = {
            "dept_name": "FINANCE",
            "total_insert": total_insert,
            "total_replace": total_replace,
            "total_unchanged": total_unchanged,
            "total_row_excel": total_row_excel,
            "preview_insert": preview_insert,
            "preview_replace": preview_replace 
        }
        record.status = StatusEnum.AWAITING_PREVIEW
        self.db.commit()

    # # ======================================================================================
    # # PYTHON COMMIT
    # # =====================================================================================
    # def execute_commit(self, history_id: int, filename: str):
    #     record = self.db.query(HistoryUpload).get(history_id)
    #     config = get_dept_config(self.id_dept)
        
    #     try:
    #         df_excel = self._download_and_clean(history_id, filename, self.id_dept, config["cleanser"])
            
    #         text_cols = [
    #             "idx_category", "category", "idx_sub_category", 
    #             "sub_category", "sub_sub_category", "account_name", "report_type"
    #         ]
            
    #         df_excel = df_excel.with_columns([
    #             pl.col(c).fill_null("") for c in text_cols if c in df_excel.columns
    #         ])

    #         keys = config["unique_keys"]
    #         df_excel = df_excel.unique(subset=keys, keep="last")

    #         # 2. Sekarang baru konversi ke dicts
    #         data_dicts = df_excel.to_dicts()

    #         # 3. Siapkan Model SQLAlchemy (sisanya tetap sama)
    #         TargetModel = config["model"]
    #         stmt = insert(TargetModel).values(data_dicts)

    #         pk_name = TargetModel.__mapper__.primary_key[0].name
    #         update_dict = {
    #             c.name: c for c in stmt.excluded if c.name != pk_name
    #         }
            
    #         upsert_stmt = stmt.on_conflict_do_update(
    #             constraint=config["constraint_name"], 
    #             set_=update_dict
    #         )

    #         # 4. Tembak ke Database
    #         self.db.execute(upsert_stmt)
            
    #         # record.status = StatusEnum.PENDING 
    #         record.status = StatusEnum.PENDING
    #         self.db.commit()

    #         # try:
    #         #     # Gunakan text() untuk query mentah
    #         #     self.db.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY olap_finance.mv_finance_detail;"))
    #         #     self.db.commit() 
    #         #     print("Materialized View refreshed successfully.")
    #         # except Exception as mv_e:
    #         #     self.db.rollback() 
    #         #     print(f"Warning: Materialized View refresh failed: {mv_e}")

    #     except Exception as e:
    #         self.db.rollback()
    #         record.status = StatusEnum.FAILED
    #         self.db.commit()
    #         raise e


    # # ======================================================================================
    # # POSTGRES COMMIT
    # # =====================================================================================
    def execute_commit(self, history_id: int, filename: str):
        record = self.db.query(HistoryUpload).get(history_id)
        config = get_dept_config(self.id_dept)
        
        # Nama staging table yang sudah dibuat saat analyze
        stg_table = f"stg_finance_upload_{history_id}"
        target_table = "oltp_tes.fact_finance"
        
        try:
            # Ambil kolom dari registry atau dari tabel staging langsung
            # Kita asumsikan kolomnya sama dengan fact_finance
            columns = [
                "bulan", "account_name", "report_type", "idx_category", 
                "category", "idx_sub_category", "sub_category", 
                "sub_sub_category", "value", "id_history"
            ]
            
            cols_str = ", ".join(columns)
            # Exclude primary key dan unique keys dari update
            update_cols = [c for c in columns if c not in config["unique_keys"]]
            excluded_str = ", ".join([f"{c} = EXCLUDED.{c}" for c in update_cols])

            # EKSEKUSI PINDAH DATA (Sangat cepat, hitungan milidetik)
            upsert_query = text(f"""
                INSERT INTO {target_table} ({cols_str})
                SELECT {cols_str} FROM {stg_table}
                ON CONFLICT ON CONSTRAINT {config["constraint_name"]}
                DO UPDATE SET {excluded_str};
            """)

            self.db.execute(upsert_query)
            
            # BARU DI SINI HAPUS STAGING-NYA
            self.db.execute(text(f"DROP TABLE IF EXISTS {stg_table}"))
            
            record.status = StatusEnum.PENDING # atau PENDING jika ada proses lain
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            # Jika gagal, staging jangan dihapus dulu supaya bisa di-retry
            record.status = StatusEnum.FAILED
            self.db.commit()
            raise e
        


    def execute_cancel(self, history_id: int):
        # Nama staging table yang sama
        stg_table = f"stg_finance_upload_{history_id}"
        
        try:
            # Hapus tabel staging jika ada
            self.db.execute(text(f"DROP TABLE IF EXISTS {stg_table}"))
            
            # Update status di history upload
            record = self.db.query(HistoryUpload).filter(HistoryUpload.id_history_upload == history_id).first()
            if record:
                record.status = StatusEnum.CANCELLED
                
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e