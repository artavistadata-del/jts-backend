import polars as pl
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import text
from src.workers.cleaning.base_cleaning_service import BaseCleaningService
from src.workers.cleanser.finance_cleanser import process_finance_excel
from src.config.config import engine 
from src.config.dept_registry import get_dept_config
from src.models.models.models import HistoryUpload, StatusEnum, FactFinance

class FinanceService(BaseCleaningService):
    def __init__(self, db_session):
        super().__init__(db_session)
        self.id_dept = 1
        self.unique_keys = [
            "bulan", "account_name", "report_type", 
            "idx_category", "category", "idx_sub_category", 
            "sub_category", "sub_sub_category"
        ]
        self.stg_schema = "stg_table"

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
        stg_table = f"{self.stg_schema}.stg_finance_upload_{history_id}"
        
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
                LEFT JOIN oltp_main.fact_finance f ON {join_conditions}
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
                JOIN oltp_main.fact_finance f ON {join_conditions}
                WHERE s.value != f.value
            """)
            
            df_replace = pl.read_database(query=query_replace, connection=engine)
            total_replace = df_replace.height
            preview_replace = df_replace.head(10).cast(pl.String).to_dicts()

            # Hitung total unchanged
            total_unchanged = total_row_excel - (total_insert + total_replace)


            # ==========================================
            # C. DETEKSI HUMAN ERROR (WIP MISMATCH)
            # ==========================================
            query_wip_mismatch = text(f"""
                WITH StagingBeginning AS (
                    SELECT bulan, value 
                    FROM {stg_table} 
                    WHERE account_name = '1 WIP BEGINNING BALANCE'
                ),
                EndingCombined AS (
                    -- Prioritas 1: Ambil WIP Ending dari file Excel yang SEDANG di-upload
                    SELECT bulan, value 
                    FROM {stg_table} 
                    WHERE account_name = '2 WIP ENDING BALANCE'
                    
                    UNION ALL
                    
                    -- Prioritas 2: Ambil WIP Ending dari Database Utama 
                    -- (Hanya jika bulannya tidak ada di file Excel)
                    SELECT bulan, value 
                    FROM oltp_main.fact_finance f
                    WHERE account_name = '2 WIP ENDING BALANCE'
                      AND NOT EXISTS (
                          SELECT 1 FROM {stg_table} s 
                          WHERE s.account_name = '2 WIP ENDING BALANCE' 
                          AND s.bulan = f.bulan
                      )
                )
                SELECT 
                    sb.bulan AS bulan_upload,
                    sb.value AS nilai_beginning_baru,
                    ec.value AS nilai_ending_lama
                FROM StagingBeginning sb
                LEFT JOIN EndingCombined ec 
                    -- Cocokkan bulan Beginning dengan bulan Ending (1 bulan mundur)
                    ON ec.bulan = (sb.bulan - INTERVAL '1 month')::DATE
                -- Filter hanya yang nilainya beda ATAU tidak ketemu sama sekali
                WHERE ABS(sb.value) != ABS(ec.value) OR ec.value IS NULL
            """)
            
            wip_mismatch_results = self.db.execute(query_wip_mismatch).fetchall()
            
            # Kumpulkan daftar peringatan untuk dikirim ke UI
            warnings = []
            for row in wip_mismatch_results:
                val_beg = f"{row.nilai_beginning_baru:,.2f}" if row.nilai_beginning_baru else "0"
                
                if row.nilai_ending_lama is None:
                    warnings.append(f"⚠️ {row.bulan_upload}: Data WIP Ending bulan lalu tidak ditemukan.")
                else:
                    val_end = f"{row.nilai_ending_lama:,.2f}"
                    warnings.append(f"⚠️ {row.bulan_upload}: WIP Beg ({val_beg}) ≠ WIP End bln lalu ({val_end}).")

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
            "preview_replace": preview_replace,
            "warnings": warnings
        }
        record.status = StatusEnum.AWAITING_PREVIEW
        self.db.commit()

    # # ======================================================================================
    # # POSTGRES COMMIT
    # # =====================================================================================
    def execute_commit(self, history_id: int, filename: str):
        record = self.db.query(HistoryUpload).get(history_id)
        config = get_dept_config(self.id_dept)
        
        # Nama staging table yang sudah dibuat saat analyze
        stg_table = f"{self.stg_schema}.stg_finance_upload_{history_id}"
        target_table = "oltp_main.fact_finance"
        
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
        stg_table = f"{self.stg_schema}.stg_finance_upload_{history_id}"
        
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