# cleaning/cleaning_service.py

import io
import polars as pl
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from config.minio_conf import minio_client
from config.config import engine 
from models.models.models import HistoryUpload, StatusEnum

# Import otak konfigurasi yang kita buat tadi
from config.dept_registry import get_dept_config 

class BaseCleaningService:
    def __init__(self, db_session):
        self.db = db_session
        self.minio = minio_client

    def _download_and_clean(self, history_id: int, filename: str, id_dept: int, config: dict) -> pl.DataFrame:
        """Helper dinamis: Unduh dari MinIO, bersihkan pakai fungsi dari config."""
        # Asumsi bucket MinIO kamu dinamakan berdasarkan ID Dept
        raw_bucket = f"raw-dept-{id_dept}" 
        
        response = self.minio.get_object(raw_bucket, filename)
        raw_bytes = io.BytesIO(response.read())
        response.close()
        response.release_conn()

        # Panggil fungsi cleanser spesifik yang terdaftar di registry
        cleanser_func = config["cleanser"]
        return cleanser_func(raw_bytes, history_id)

    # # ==========================================
    # # TAHAP 1.1: PREVIEW (Cek Replace vs Insert)
    # # ==========================================
    def execute_analyze(self, history_id: int, filename: str, id_dept: int):
        config = get_dept_config(id_dept)
        df_excel = self._download_and_clean(history_id, filename, id_dept, config)
        
        keys = config["unique_keys"]
        table_name = config["table_name"]
        query = f"""
            SELECT 
                bulan, account_name, report_type, 
                idx_category, category, 
                idx_sub_category, sub_category, sub_sub_category,
                value 
            FROM {table_name}
        """
        df_db = pl.read_database(query=query, connection=engine)

        # 3. Paksa Schema (Agar tidak error jika database kosong)
        df_db = df_db.with_columns([
            pl.col("bulan").cast(pl.Date),
            pl.col("value").cast(pl.Float64),
            pl.col("account_name").cast(pl.String),
            pl.col("report_type").cast(pl.String),
            pl.col("idx_category").cast(pl.String),
            pl.col("category").cast(pl.String),
            pl.col("idx_sub_category").cast(pl.String),
            pl.col("sub_category").cast(pl.String),
            pl.col("sub_sub_category").cast(pl.String)
        ])

        string_keys = [
            "account_name", "report_type", "idx_category", "category", 
            "idx_sub_category", "sub_category", "sub_sub_category"
        ]

        df_excel = df_excel.with_columns([pl.col(c).fill_null("") for c in string_keys])
        df_db = df_db.with_columns([pl.col(c).fill_null("") for c in string_keys])
        # 3. Join Excel dengan Database untuk Deteksi Perubahan



        # ===============================
        # Ini ini kalo mau nampilkan preview
        # ===============================
        
        # 3. Join Excel dengan Database untuk Deteksi Perubahan
        df_compare = df_excel.join(df_db, on=keys, how="left", suffix="_db")

        # A. Deteksi Data Baru (Insert)
        df_insert = df_compare.filter(pl.col("value_db").is_null())
        total_insert = df_insert.height

        # B. Deteksi Data Berubah (Replace/Update)
        df_replace = df_compare.filter(
            (pl.col("value_db").is_not_null()) & 
            (pl.col("value") != pl.col("value_db"))
        )
        total_replace = df_replace.height

        # C. Deteksi Data Sama (Unchanged/Ignored)
        total_unchanged = df_compare.filter(
            (pl.col("value_db").is_not_null()) & 
            (pl.col("value") == pl.col("value_db"))
        ).height

        # ==========================================
        # SIAPKAN PREVIEW DATA (Max 10 Baris)
        # ==========================================
        original_cols = df_excel.columns # Ambil nama kolom asli (buang kolom '_db')
        
        # Kita cast ke pl.String agar aman saat diubah menjadi JSON (mencegah error format Date)
        preview_insert = (
            df_insert.select(original_cols)
            .head(10)
            .cast(pl.String)
            .to_dicts()
        )
        
        preview_replace = (
            df_replace.select(original_cols)
            .head(10)
            .cast(pl.String)
            .to_dicts()
        )

        # 4. Simpan Hasil ke History Upload
        record = self.db.query(HistoryUpload).filter(HistoryUpload.id_history_upload == history_id).first()
        record.analysis_result = {
            "dept_name": config.get("dept_name", "Unknown"),
            "total_insert": total_insert,
            "total_replace": total_replace,
            "total_unchanged": total_unchanged,
            "total_row_excel": df_excel.height,
            "preview_insert": preview_insert,
            "preview_replace": preview_replace 
        }
        record.status = StatusEnum.AWAITING_PREVIEW
        self.db.commit()

        # # ===============================
        # # Ini ini kalo mau nampilkan count aja
        # # ===============================
        # # Kita beri suffix '_db' pada kolom value dari database agar tidak bentrok
        # df_compare = df_excel.join(df_db, on=keys, how="left", suffix="_db")

        # # A. Deteksi Data Baru (Insert)
        # # Ciri: Tidak ditemukan di DB (kolom value_db nya null)
        # total_insert = df_compare.filter(pl.col("value_db").is_null()).height

        # # B. Deteksi Data Berubah (Replace/Update)
        # # Ciri: Ada di DB (value_db tidak null) TAPI nilainya beda dengan Excel
        # total_replace = df_compare.filter(
        #     (pl.col("value_db").is_not_null()) & 
        #     (pl.col("value") != pl.col("value_db"))
        # ).height

        # # C. Deteksi Data Sama (Unchanged/Ignored)
        # # Ciri: Ada di DB dan nilainya sama persis
        # total_unchanged = df_compare.filter(
        #     (pl.col("value_db").is_not_null()) & 
        #     (pl.col("value") == pl.col("value_db"))
        # ).height

        # # 4. Simpan Hasil ke History Upload
        # record = self.db.query(HistoryUpload).filter(HistoryUpload.id_history_upload == history_id).first()
        # record.analysis_result = {
        #     "dept_name": config["dept_name"],
        #     "total_insert": total_insert,
        #     "total_replace": total_replace,
        #     "total_unchanged": total_unchanged, # Beri tahu user ada data yang diabaikan
        #     "total_row_excel": df_excel.height
        # }
        # record.status = StatusEnum.AWAITING_PREVIEW
        # self.db.commit()

    # ==========================================
    # TAHAP 2: COMMIT (Upsert Permanen)
    # ==========================================
    def execute_commit(self, history_id: int, filename: str, id_dept: int):
        record = self.db.query(HistoryUpload).get(history_id)
        config = get_dept_config(id_dept)
        
        try:
            # 1. Tarik dan bersihkan ulang
            df_excel = self._download_and_clean(history_id, filename, id_dept, config)
            
            # --- TAMBAHKAN LOGIKA INI (1b) ---
            # A. Daftar kolom teks yang tidak boleh NULL di database
            text_cols = [
                "idx_category", "category", "idx_sub_category", 
                "sub_category", "sub_sub_category", "account_name", "report_type"
            ]
            
            # B. Isi NULL dengan string kosong agar tidak melanggar NotNullViolation
            df_excel = df_excel.with_columns([
                pl.col(c).fill_null("") for c in text_cols if c in df_excel.columns
            ])

            # C. Hapus duplikat internal Excel agar tidak kena CardinalityViolation
            keys = config["unique_keys"]
            df_excel = df_excel.unique(subset=keys, keep="last")
            # ---------------------------------

            # 2. Sekarang baru konversi ke dicts
            data_dicts = df_excel.to_dicts()

            # 3. Siapkan Model SQLAlchemy (sisanya tetap sama)
            TargetModel = config["model"]
            stmt = insert(TargetModel).values(data_dicts)

            pk_name = TargetModel.__mapper__.primary_key[0].name
            update_dict = {
                c.name: c for c in stmt.excluded if c.name != pk_name
            }
            
            upsert_stmt = stmt.on_conflict_do_update(
                constraint=config["constraint_name"], 
                set_=update_dict
            )

            # 4. Tembak ke Database
            self.db.execute(upsert_stmt)
            
            # record.status = StatusEnum.PENDING 
            record.status = StatusEnum.APPROVED
            self.db.commit()

            try:
                # Gunakan text() untuk query mentah
                self.db.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY olap_finance.mv_finance_detail;"))
                self.db.commit() 
                print("Materialized View refreshed successfully.")
            except Exception as mv_e:
                self.db.rollback() 
                print(f"Warning: Materialized View refresh failed: {mv_e}")

        except Exception as e:
            self.db.rollback()
            record.status = StatusEnum.FAILED
            self.db.commit()
            raise e