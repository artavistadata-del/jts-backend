import polars as pl
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import text
from src.workers.cleaning.base_cleaning_service import BaseCleaningService
from src.workers.cleanser.finance import process_finance_excel
from src.core.database import engine 
from src.modules.departments.registry import get_dept_config
from src.models.models import History, StatusEnum, FactFinance

class FinanceService(BaseCleaningService):
    def __init__(self, db_session):
        super().__init__(db_session)
        self.id_dept = 1
        # [UPDATE 1] Tambahkan actual_budget ke unique_keys
        self.unique_keys = [
            "bulan", "account_name", "report_type", "actual_budget",
            "idx_category", "category", "idx_sub_category", 
            "sub_category", "sub_sub_category"
        ]
        self.stg_schema = "stg_table"

    # ===========================================================================================
    # POSTGRES COMPARE
    # ===========================================================================================
    def execute_analyze(self, history_id: int, filename: str):
        # Ambil record SATU KALI di awal
        record = self.db.query(History).filter(History.id == history_id).first()
        if not record:
            raise ValueError(f"Data history upload dengan ID {history_id} tidak ditemukan.")

        try:
            # 1. Bersihkan Data Excel (Bisa melempar ValueError jika format salah)
            df_excel = self._download_and_clean(history_id, filename, self.id_dept, process_finance_excel)
            
            # Isi null values agar SQL tidak bingung saat JOIN
            string_keys = self.unique_keys[1:] 
            df_excel = df_excel.with_columns([pl.col(c).fill_null("") for c in string_keys])
            total_row_excel = df_excel.height

            # 2. PUSH KE STAGING TABLE
            stg_table = f"{self.stg_schema}.stg_finance_upload_{history_id}"
            db_uri = f"postgresql://{engine.url.username}:{engine.url.password}@{engine.url.host}:{engine.url.port}/{engine.url.database}"
            
            df_excel.write_database(
                table_name=stg_table, 
                connection=db_uri, 
                if_table_exists="replace",
                engine="adbc"
            )

            # 3. SUSUN KONDISI JOIN
            join_conditions = " AND ".join([f"s.{key} = f.{key}" for key in self.unique_keys])

            # ==========================================
            # A. HITUNG & AMBIL PREVIEW INSERT
            # ==========================================
            query_insert = text(f"""
                SELECT s.* FROM {stg_table} s
                LEFT JOIN oltp_main.fact_finance f ON {join_conditions}
                WHERE f.bulan IS NULL
            """)
            
            df_insert = pl.read_database(query=query_insert, connection=engine)
            total_insert = df_insert.height
            preview_insert = df_insert.head(10).cast(pl.String).to_dicts()

            # ==========================================
            # B. HITUNG & AMBIL PREVIEW REPLACE
            # ==========================================
            query_replace = text(f"""
                SELECT s.* FROM {stg_table} s
                JOIN oltp_main.fact_finance f ON {join_conditions}
                WHERE s.value != f.value
            """)
            
            df_replace = pl.read_database(query=query_replace, connection=engine)
            total_replace = df_replace.height
            preview_replace = df_replace.head(10).cast(pl.String).to_dicts()

            # Hitung total unchanged
            total_unchanged = total_row_excel - (total_insert + total_replace)

            # ==========================================
            # C. DETEKSI HUMAN ERROR (WIP MISMATCH) - HANYA UNTUK ACTUAL
            # ==========================================
            query_wip_mismatch = text(f"""
                WITH StagingBeginning AS (
                    SELECT bulan, value 
                    FROM {stg_table} 
                    WHERE account_name = '1 WIP BEGINNING BALANCE' 
                      AND actual_budget ILIKE '%%Actual%%'
                ),
                EndingCombined AS (
                    SELECT bulan, value 
                    FROM {stg_table} 
                    WHERE account_name = '2 WIP ENDING BALANCE'
                      AND actual_budget ILIKE '%%Actual%%'
                    
                    UNION ALL
                    
                    SELECT bulan, value 
                    FROM oltp_main.fact_finance f
                    WHERE account_name = '2 WIP ENDING BALANCE'
                      AND actual_budget ILIKE '%%Actual%%'
                      AND NOT EXISTS (
                          SELECT 1 FROM {stg_table} s 
                          WHERE s.account_name = '2 WIP ENDING BALANCE' 
                            AND s.actual_budget ILIKE '%%Actual%%'
                            AND s.bulan = f.bulan
                      )
                )
                SELECT 
                    sb.bulan AS bulan_upload,
                    sb.value AS nilai_beginning_baru,
                    ec.value AS nilai_ending_lama
                FROM StagingBeginning sb
                LEFT JOIN EndingCombined ec 
                    ON ec.bulan = (sb.bulan - INTERVAL '1 month')::DATE
                WHERE ABS(sb.value) != ABS(ec.value) OR ec.value IS NULL
            """)
            
            wip_mismatch_results = self.db.execute(query_wip_mismatch).fetchall()
            
            warnings = []
            for row in wip_mismatch_results:
                val_beg = f"{row.nilai_beginning_baru:,.2f}" if row.nilai_beginning_baru else "0"
                if row.nilai_ending_lama is None:
                    warnings.append(f"⚠️ {row.bulan_upload}: Data WIP Ending (Actual) bulan lalu tidak ditemukan.")
                else:
                    val_end = f"{row.nilai_ending_lama:,.2f}"
                    warnings.append(f"⚠️ {row.bulan_upload}: WIP Beg Actual ({val_beg}) ≠ WIP End bln lalu ({val_end}).")

            # 5. SIMPAN HASIL (Langsung pakai 'record' yang sudah diambil di awal)
            record.analysis_result = {
                "dept_name": "FINANCE",
                "total_insert": total_insert,
                "total_replace": total_replace,
                "total_unchanged": total_unchanged,
                "total_row_excel": total_row_excel,
                "preview_insert": preview_insert,
                "preview_replace": preview_replace,
                "warnings": warnings
            }
            record.status = StatusEnum.AWAITING_PREVIEW
            self.db.commit()

        except ValueError as ve:
            # Menangkap error validasi dari proses cleaning (Fail-Fast)
            self.db.rollback()
            record.status = StatusEnum.FAILED
            record.analysis_result = {"error": f"Terjadi kesalahan sistem: {str(ve)}"}
            self.db.commit()
            raise ve
            
        except Exception as e:
            # Menangkap error sistem database
            self.db.rollback()
            record.status = StatusEnum.FAILED
            record.notes = "Terjadi kesalahan sistem saat memproses data."
            self.db.commit()
            raise e
    # ======================================================================================
    # POSTGRES COMMIT
    # =====================================================================================
    def execute_commit(self, history_id: int, filename: str):
        record = self.db.query(History).get(history_id)
        config = get_dept_config(self.id_dept)
        
        stg_table = f"{self.stg_schema}.stg_finance_upload_{history_id}"
        target_table = "oltp_main.fact_finance"
        
        try:
            # [UPDATE 3] Tambahkan actual_budget ke list columns
            columns = [
                "bulan", "account_name", "report_type", "actual_budget", 
                "idx_category", "category", "idx_sub_category", "sub_category", 
                "sub_sub_category", "value", "history_id"
            ]
            
            cols_str = ", ".join(columns)
            update_cols = [c for c in columns if c not in config["unique_keys"]]
            excluded_str = ", ".join([f"{c} = EXCLUDED.{c}" for c in update_cols])

            upsert_query = text(f"""
                INSERT INTO {target_table} ({cols_str})
                SELECT {cols_str} FROM {stg_table}
                ON CONFLICT ON CONSTRAINT {config["constraint_name"]}
                DO UPDATE SET {excluded_str};
            """)

            self.db.execute(upsert_query)
            self.db.execute(text(f"DROP TABLE IF EXISTS {stg_table}"))
            
            record.status = StatusEnum.PENDING 
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            record.status = StatusEnum.FAILED
            record.analysis_result = {
                "error": "Gagal melakukan Upsert ke database utama.", 
                "detail": str(e)
            }
            self.db.commit()
            raise e

    def execute_cancel(self, history_id: int, filename: str):
        stg_table = f"{self.stg_schema}.stg_finance_upload_{history_id}"
        try:
            self.db.execute(text(f"DROP TABLE IF EXISTS {stg_table}"))
            record = self.db.query(History).filter(History.id == history_id).first()
            if record:
                record.status = StatusEnum.CANCELLED
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e