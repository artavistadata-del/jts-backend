import polars as pl
from sqlalchemy import text

from src.workers.cleaning.base_cleaning_service import BaseCleaningService
from src.workers.cleanser.purchasing import process_purchasing_excel
from src.core.database import engine
from src.models.models import History, StatusEnum


class PurchasingService(BaseCleaningService):
    def __init__(self, db_session):
        super().__init__(db_session)
        self.id_dept = 3
        self.stg_schema = "stg_table"

    def execute_analyze(self, history_id: int, filename: str):
        record = self.db.query(History).filter(History.id == history_id).first()

        if not record:
            raise ValueError(f"Data history upload dengan ID {history_id} tidak ditemukan.")

        try:
            dfs = self._download_and_clean(
                history_id=history_id,
                filename=filename,
                id_dept=self.id_dept,
                cleanser_func=process_purchasing_excel,
            )

            db_uri = (
                f"postgresql://{engine.url.username}:{engine.url.password}"
                f"@{engine.url.host}:{engine.url.port}/{engine.url.database}"
            )

            staging_tables = {
                "sheet1": f"{self.stg_schema}.stg_purchasing_sheet1_upload_{history_id}",
                "sheet2": f"{self.stg_schema}.stg_purchasing_sheet2_upload_{history_id}",
                "sheet3": f"{self.stg_schema}.stg_purchasing_sheet3_upload_{history_id}",
            }

            # Write semua sheet ke staging
            for sheet_name, df in dfs.items():
                df.write_database(
                    table_name=staging_tables[sheet_name],
                    connection=db_uri,
                    if_table_exists="replace",
                    engine="adbc",
                )

            record.analysis_result = {
                "dept_name": "PURCHASING",
                "sheet1_rows": dfs["sheet1"].height,
                "sheet2_rows": dfs["sheet2"].height,
                "sheet3_rows": dfs["sheet3"].height,
                "sheet1_preview": dfs["sheet1"].head(5).cast(pl.String).to_dicts(),
                "sheet2_preview": dfs["sheet2"].head(5).cast(pl.String).to_dicts(),
                "sheet3_preview": dfs["sheet3"].head(10).cast(pl.String).to_dicts(),
                "staging_tables": staging_tables,
            }

            record.status = StatusEnum.AWAITING_PREVIEW
            self.db.commit()

        except ValueError as ve:
            self.db.rollback()
            record.status = StatusEnum.FAILED
            record.analysis_result = {"error": str(ve)}
            self.db.commit()
            raise ve

        except Exception as e:
            self.db.rollback()
            record.status = StatusEnum.FAILED
            record.analysis_result = {
                "error": "Terjadi kesalahan sistem saat cleansing Purchasing.",
                "detail": str(e),
            }
            self.db.commit()
            raise e

    def execute_commit(self, history_id: int, filename: str):
        record = self.db.query(History).filter(History.id == history_id).first()

        if not record:
            raise ValueError(f"Data history upload dengan ID {history_id} tidak ditemukan.")

        stg_sheet1 = f"{self.stg_schema}.stg_purchasing_sheet1_upload_{history_id}"
        stg_sheet2 = f"{self.stg_schema}.stg_purchasing_sheet2_upload_{history_id}"
        stg_sheet3 = f"{self.stg_schema}.stg_purchasing_sheet3_upload_{history_id}"

        try:
            # Biar idempotent kalau task kepanggil ulang:
            # hapus dulu data final untuk history_id yang sama
            self.db.execute(text("""
                DELETE FROM oltp_main.purchasing_sheet1
                WHERE history_id = :history_id
            """), {"history_id": history_id})

            self.db.execute(text("""
                DELETE FROM oltp_main.purchasing_sheet2
                WHERE history_id = :history_id
            """), {"history_id": history_id})

            self.db.execute(text("""
                DELETE FROM oltp_main.purchasing_sheet3
                WHERE history_id = :history_id
            """), {"history_id": history_id})

            # Insert sheet 1
            self.db.execute(text(f"""
                INSERT INTO oltp_main.purchasing_sheet1 (
                    history_id,
                    price_date,
                    tex_us_no_1h_cfr_korea_domestic_cost,
                    lme_usno_1_2_80_20_cfr_turkey_domestic_cost,
                    local_price_usd,
                    busheling_contract_usd,
                    pns_contract_usd,
                    hms_contract_usd,
                    shr_contract_usd,
                    local_price_idr,
                    usd_rate,
                    idr_rate,
                    idr_usd_exchange_rate,
                    us_no_1h_cfr_korea,
                    lme_usno_1_2_80_20_cfr_turky,
                    lme_usno_1_2_80_20_cfr_turkey,
                    local_premium_idr_per_kg
                )
                SELECT
                    history_id,
                    price_date,
                    tex_us_no_1h_cfr_korea_domestic_cost,
                    lme_usno_1_2_80_20_cfr_turkey_domestic_cost,
                    local_price_usd,
                    busheling_contract_usd,
                    pns_contract_usd,
                    hms_contract_usd,
                    shr_contract_usd,
                    local_price_idr,
                    usd_rate,
                    idr_rate,
                    idr_usd_exchange_rate,
                    us_no_1h_cfr_korea,
                    lme_usno_1_2_80_20_cfr_turky,
                    lme_usno_1_2_80_20_cfr_turkey,
                    local_premium_idr_per_kg
                FROM {stg_sheet1}
            """))

            # Insert sheet 2
            self.db.execute(text(f"""
                INSERT INTO oltp_main.purchasing_sheet2 (
                    history_id,
                    variety,
                    list_no,
                    contract_date,
                    supplier,
                    origin,
                    ton,
                    price_usd_per_ton_cif,
                    total_usd,
                    grade,
                    delivery_detail,
                    delivery,
                    actual_eta,
                    delivery_remarks,
                    avg_qty,
                    avg_value,
                    avg_price
                )
                SELECT
                    history_id,
                    variety,
                    list_no,
                    contract_date,
                    supplier,
                    origin,
                    ton,
                    price_usd_per_ton_cif,
                    total_usd,
                    grade,
                    delivery_detail,
                    delivery,
                    actual_eta,
                    delivery_remarks,
                    avg_qty,
                    avg_value,
                    avg_price
                FROM {stg_sheet2}
            """))

            # Insert sheet 3
            self.db.execute(text(f"""
                INSERT INTO oltp_main.purchasing_sheet3 (
                    history_id,
                    source_index,
                    variety,
                    detail,
                    price_date,
                    value
                )
                SELECT
                    history_id,
                    source_index,
                    variety,
                    detail,
                    price_date,
                    value
                FROM {stg_sheet3}
            """))

            # Drop staging tables
            self.db.execute(text(f"DROP TABLE IF EXISTS {stg_sheet1}"))
            self.db.execute(text(f"DROP TABLE IF EXISTS {stg_sheet2}"))
            self.db.execute(text(f"DROP TABLE IF EXISTS {stg_sheet3}"))

            record.status = StatusEnum.PENDING
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            record.status = StatusEnum.FAILED
            record.analysis_result = {
                "error": "Gagal commit data Purchasing.",
                "detail": str(e),
            }
            self.db.commit()
            raise e

    def execute_cancel(self, history_id: int, filename: str):
        stg_sheet1 = f"{self.stg_schema}.stg_purchasing_sheet1_upload_{history_id}"
        stg_sheet2 = f"{self.stg_schema}.stg_purchasing_sheet2_upload_{history_id}"
        stg_sheet3 = f"{self.stg_schema}.stg_purchasing_sheet3_upload_{history_id}"

        try:
            self.db.execute(text(f"DROP TABLE IF EXISTS {stg_sheet1}"))
            self.db.execute(text(f"DROP TABLE IF EXISTS {stg_sheet2}"))
            self.db.execute(text(f"DROP TABLE IF EXISTS {stg_sheet3}"))

            record = self.db.query(History).filter(History.id == history_id).first()
            if record:
                record.status = StatusEnum.CANCELLED

            self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise e
