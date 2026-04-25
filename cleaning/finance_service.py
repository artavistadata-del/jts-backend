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

    def execute_analyze(self, history_id: int, filename: str):
        df_excel = self._download_and_clean(history_id, filename, self.id_dept, process_finance_excel)
        
        query = """
            SELECT bulan, account_name, report_type, idx_category, category, 
                   idx_sub_category, sub_category, sub_sub_category, value 
            FROM oltp_tes.fact_finance
        """

        df_db = pl.read_database(query=query, connection=engine)

        df_db = df_db.with_columns([
            pl.col("bulan").cast(pl.Date), pl.col("value").cast(pl.Float64),
            pl.col("account_name").cast(pl.String), pl.col("report_type").cast(pl.String),
            pl.col("idx_category").cast(pl.String), pl.col("category").cast(pl.String),
            pl.col("idx_sub_category").cast(pl.String), pl.col("sub_category").cast(pl.String),
            pl.col("sub_sub_category").cast(pl.String)
        ])

        string_keys = self.unique_keys[1:] 
        df_excel = df_excel.with_columns([pl.col(c).fill_null("") for c in string_keys])
        df_db = df_db.with_columns([pl.col(c).fill_null("") for c in string_keys])

        df_compare = df_excel.join(df_db, on=self.unique_keys, how="left", suffix="_db")
        
        df_insert = df_compare.filter(pl.col("value_db").is_null())
        total_insert = df_insert.height

        df_replace = df_compare.filter(
            (pl.col("value_db").is_not_null()) & 
            (pl.col("value") != pl.col("value_db"))
        )
        total_replace = df_replace.height

        total_unchanged = df_compare.filter(
            (pl.col("value_db").is_not_null()) & 
            (pl.col("value") == pl.col("value_db"))
        ).height

        # ==========================================
        # SIAPKAN PREVIEW DATA (Max 10 Baris)
        # ==========================================
        original_cols = df_excel.columns
        
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
            "dept_name": "FINANCE",
            "total_insert": total_insert,
            "total_replace": total_replace,
            "total_unchanged": total_unchanged,
            "total_row_excel": df_excel.height,
            "preview_insert": preview_insert,
            "preview_replace": preview_replace 
        }
        record.status = StatusEnum.AWAITING_PREVIEW
        self.db.commit()

    def execute_commit(self, history_id: int, filename: str):
        record = self.db.query(HistoryUpload).get(history_id)
        config = get_dept_config(self.id_dept)
        
        try:
            df_excel = self._download_and_clean(history_id, filename, self.id_dept, config["cleanser"])
            
            text_cols = [
                "idx_category", "category", "idx_sub_category", 
                "sub_category", "sub_sub_category", "account_name", "report_type"
            ]
            
            df_excel = df_excel.with_columns([
                pl.col(c).fill_null("") for c in text_cols if c in df_excel.columns
            ])

            keys = config["unique_keys"]
            df_excel = df_excel.unique(subset=keys, keep="last")

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