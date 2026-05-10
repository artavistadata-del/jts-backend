from sqlalchemy import text
from src.core.database import engine
from src.models.models import History, StatusEnum
from src.workers.cleaning.abstract_cleaning import AbstractCleaningService
from src.workers.cleanser.finance import process_finance_excel
import polars as pl


def normalize_key_expr(col_name: str) -> pl.Expr:
    return (
        pl.col(col_name)
        .cast(pl.String)
        .fill_null("")
        .str.strip_chars()
        .str.replace_all('"', "")
        .str.replace_all(r"\s+", " ")
        .str.to_uppercase()
    )


class FinService(AbstractCleaningService):
    def __init__(self, db_session):
        super().__init__(db_session)

        self.id_dept = 1

        # Sesuaikan jika table final kamu ada di schema oltp
        self.main_table = "oltp_main.finance_transactions"
        self.stg_table = "stg_table.finance_transactions"

        self.rule_lookup_view = "oltp_main.vw_finance_transaction_rule_lookup"

        self.join_cols = [
            "sheet_name",
            "category_name",
            "sub_category_name",
            "sub_sub_category_name",
            "account_name",
            "actual_budget",
        ]

    # ============================================================
    # ANALYZE
    # ============================================================
    def execute_analyze(self, history_id: int, filename: str):
        record = self.db.query(History).filter(History.id == history_id).first()

        if not record:
            raise ValueError("Data History Upload tidak ditemukan.")

        try:
            self.df_rule = None
            self.df_mapped = None

            self._pull_data(history_id, filename)
            self._mapping_data(history_id, filename)
            total_row_excel = self._push_data(history_id, filename)

            # ==============================
            # PREVIEW INSERT
            # ==============================
            query_insert = text(f"""
                SELECT s.*
                FROM {self.stg_table} s
                LEFT JOIN {self.main_table} f
                    ON s.rule_id = f.rule_id
                   AND s.period_month = f.period_month
                WHERE s.history_id = :history_id
                  AND f.id IS NULL
            """)

            df_insert = pl.read_database(
                query=query_insert,
                connection=engine,
                execute_options={"parameters": {"history_id": history_id}},
            )

            total_insert = df_insert.height
            preview_insert = df_insert.head(10).cast(pl.String).to_dicts()

            # ==============================
            # PREVIEW REPLACE
            # ==============================
            query_replace = text(f"""
                SELECT
                    s.*,
                    f.amount AS old_amount
                FROM {self.stg_table} s
                JOIN {self.main_table} f
                    ON s.rule_id = f.rule_id
                   AND s.period_month = f.period_month
                WHERE s.history_id = :history_id
                  AND s.amount IS DISTINCT FROM f.amount
            """)

            df_replace = pl.read_database(
                query=query_replace,
                connection=engine,
                execute_options={"parameters": {"history_id": history_id}},
            )

            total_replace = df_replace.height
            preview_replace = df_replace.head(10).cast(pl.String).to_dicts()

            total_unchanged = total_row_excel - (total_insert + total_replace)

            record.analysis_result = {
                "dept_name": "FINANCE",
                "total_row_excel": total_row_excel,
                "total_insert": total_insert,
                "total_replace": total_replace,
                "total_unchanged": total_unchanged,
                "preview_insert": preview_insert,
                "preview_replace": preview_replace,
                "warnings": [],
            }

            record.status = StatusEnum.AWAITING_PREVIEW
            self.db.commit()

        except ValueError as ve:
            self.db.rollback()

            record.status = StatusEnum.FAILED
            record.analysis_result = {
                "error": str(ve)
            }

            self.db.commit()
            raise ve

        except Exception as e:
            self.db.rollback()

            record.status = StatusEnum.FAILED
            record.analysis_result = {
                "error": "Terjadi kesalahan sistem saat analyze finance.",
                "detail": str(e),
            }

            self.db.commit()
            raise e

    # ============================================================
    # 1. PULL RULE LOOKUP
    # ============================================================
    def _pull_data(self, history_id: int, filename: str):
        query = text(f"""
            SELECT
                rule_id,
                sheet_name,
                category_name,
                sub_category_name,
                sub_sub_category_name,
                account_name,
                actual_budget
            FROM {self.rule_lookup_view}
        """)

        df_rule = pl.read_database(
            query=query,
            connection=engine,
        )

        if df_rule.height == 0:
            raise ValueError(
                "Rule lookup kosong. Pastikan finance_transaction_rules sudah diisi."
            )

        df_rule = df_rule.with_columns([
            normalize_key_expr("sheet_name").alias("sheet_name"),
            normalize_key_expr("category_name").alias("category_name"),
            normalize_key_expr("sub_category_name").alias("sub_category_name"),
            normalize_key_expr("sub_sub_category_name").alias("sub_sub_category_name"),
            normalize_key_expr("account_name").alias("account_name"),
            normalize_key_expr("actual_budget").alias("actual_budget"),
            pl.col("rule_id").cast(pl.Int64),
        ])

        duplicate_rule = (
            df_rule
            .group_by(self.join_cols)
            .agg(pl.len().alias("total"))
            .filter(pl.col("total") > 1)
        )

        if duplicate_rule.height > 0:
            raise ValueError(
                "Rule lookup memiliki kombinasi duplicate. "
                f"Contoh: {duplicate_rule.head(10).to_dicts()}"
            )

        self.df_rule = df_rule
        return df_rule

    # ============================================================
    # 2. MAPPING EXCEL CLEANED -> RULE_ID
    # ============================================================
    def _mapping_data(self, history_id: int, filename: str):
        if self.df_rule is None:
            self._pull_data(history_id, filename)

        df_excel = self._download_and_clean(
            history_id=history_id,
            filename=filename,
            id_dept=self.id_dept,
            cleanser_func=process_finance_excel,
        )

        # Hasil cleanser kamu:
        # sheet_type, category, sub_category, sub_sub_category,
        # account_name, actual_budget, period_month, amount

        rename_map = {
            "sheet_type": "sheet_name",
            "category": "category_name",
            "sub_category": "sub_category_name",
            "sub_sub_category": "sub_sub_category_name",
        }

        df_excel = df_excel.rename({
            old: new
            for old, new in rename_map.items()
            if old in df_excel.columns
        })

        required_cols = [
            "sheet_name",
            "category_name",
            "sub_category_name",
            "sub_sub_category_name",
            "account_name",
            "actual_budget",
            "period_month",
            "amount",
        ]

        missing_cols = [c for c in required_cols if c not in df_excel.columns]

        if missing_cols:
            raise ValueError(
                f"Kolom hasil cleansing belum lengkap: {missing_cols}"
            )

        df_excel = df_excel.with_columns([
            normalize_key_expr("sheet_name").alias("sheet_name"),
            normalize_key_expr("category_name").alias("category_name"),
            normalize_key_expr("sub_category_name").alias("sub_category_name"),
            normalize_key_expr("sub_sub_category_name").alias("sub_sub_category_name"),
            normalize_key_expr("account_name").alias("account_name"),
            normalize_key_expr("actual_budget").alias("actual_budget"),

            pl.col("period_month").cast(pl.Date, strict=False),
            pl.col("amount").cast(pl.Float64, strict=False).round(6),
        ])

        # ==============================
        # VALIDASI period_month
        # ==============================
        invalid_month = df_excel.filter(pl.col("period_month").is_null())

        if invalid_month.height > 0:
            raise ValueError(
                "Ada period_month yang kosong atau gagal parse. "
                f"Contoh: {invalid_month.head(10).to_dicts()}"
            )

        # ==============================
        # VALIDASI amount
        # ==============================
        invalid_amount = df_excel.filter(pl.col("amount").is_null())

        if invalid_amount.height > 0:
            raise ValueError(
                "Ada amount yang kosong atau gagal parse. "
                f"Contoh: {invalid_amount.head(10).to_dicts()}"
            )

        # ==============================
        # JOIN KE RULE LOOKUP
        # ==============================
        df_mapped = df_excel.join(
            self.df_rule.select(self.join_cols + ["rule_id"]),
            on=self.join_cols,
            how="left",
        )

        # ==============================
        # VALIDASI RULE_ID NULL
        # ==============================
        invalid_rule = (
            df_mapped
            .filter(pl.col("rule_id").is_null())
            .select(self.join_cols)
            .unique()
        )

        if invalid_rule.height > 0:
            raise ValueError(
                "Ada kombinasi rule yang belum terdaftar. "
                f"Contoh maksimal 50: {invalid_rule.head(50).to_dicts()}"
            )

        # ==============================
        # VALIDASI DUPLICATE DALAM FILE
        # ==============================
        duplicate_upload = (
            df_mapped
            .group_by(["rule_id", "period_month"])
            .agg(pl.len().alias("total"))
            .filter(pl.col("total") > 1)
        )

        if duplicate_upload.height > 0:
            raise ValueError(
                "File upload memiliki duplicate pada kombinasi rule_id + period_month. "
                f"Contoh: {duplicate_upload.head(20).to_dicts()}"
            )

        df_staging = df_mapped.select([
            pl.lit(history_id).cast(pl.Int64).alias("history_id"),
            pl.col("rule_id").cast(pl.Int64),
            pl.col("period_month"),
            pl.col("amount").cast(pl.Float64, strict=False).round(6),
        ])

        self.df_mapped = df_staging
        return df_staging

    # ============================================================
    # 3. PUSH TO STAGING
    # ============================================================
    def _push_data(self, history_id: int, filename: str):
        if self.df_mapped is None:
            self._mapping_data(history_id, filename)

        df_staging = self.df_mapped

        if df_staging.height == 0:
            raise ValueError("Data hasil mapping kosong.")

        self.db.execute(
            text(f"""
                DELETE FROM {self.stg_table}
                WHERE history_id = :history_id
            """),
            {"history_id": history_id},
        )
        self.db.commit()

        db_port = engine.url.port or 5432
        
        db_uri = f"postgresql://{engine.url.username}:{engine.url.password}@{engine.url.host}:{db_port}/{engine.url.database}"

        df_staging.write_database(
            table_name=self.stg_table,
            connection=db_uri,
            if_table_exists="append",
            engine="sqlalchemy",
        )

        return df_staging.height

    # ============================================================
    # COMMIT
    # ============================================================
    def execute_commit(self, history_id: int, filename: str):
        record = self.db.query(History).filter(History.id == history_id).first()

        if not record:
            raise ValueError("Data History Upload tidak ditemukan.")

        try:
            count_staging = self.db.execute(
                text(f"""
                    SELECT COUNT(*)
                    FROM {self.stg_table}
                    WHERE history_id = :history_id
                """),
                {"history_id": history_id},
            ).scalar()

            if count_staging == 0:
                raise ValueError(
                    "Data staging tidak ditemukan. Kemungkinan upload belum dianalisis atau sudah dicancel."
                )

            upsert_query = text(f"""
                INSERT INTO {self.main_table} (
                    history_id,
                    rule_id,
                    period_month,
                    amount
                )
                SELECT
                    history_id,
                    rule_id,
                    period_month,
                    amount
                FROM {self.stg_table}
                WHERE history_id = :history_id
                ON CONFLICT (
                    rule_id,
                    period_month
                )
                DO UPDATE SET
                    history_id = EXCLUDED.history_id,
                    amount = EXCLUDED.amount,
                    updated_at = now()
            """)

            self.db.execute(upsert_query, {"history_id": history_id})

            self.db.execute(
                text(f"""
                    DELETE FROM {self.stg_table}
                    WHERE history_id = :history_id
                """),
                {"history_id": history_id},
            )

            record.status = StatusEnum.PENDING
            self.db.commit()

        except ValueError as ve:
            self.db.rollback()

            record.status = StatusEnum.FAILED
            record.analysis_result = {
                "error": str(ve)
            }

            self.db.commit()
            raise ve

        except Exception as e:
            self.db.rollback()

            record.status = StatusEnum.FAILED
            record.analysis_result = {
                "error": "Gagal commit finance transaction.",
                "detail": str(e),
            }

            self.db.commit()
            raise e
        

    # ============================================================
    # CANCEL
    # ============================================================
    def execute_cancel(self, history_id: int, filename: str):
        record = self.db.query(History).filter(History.id == history_id).first()

        if not record:
            raise ValueError("Data History Upload tidak ditemukan.")

        try:
            self.db.execute(
                text(f"""
                    DELETE FROM {self.stg_table}
                    WHERE history_id = :history_id
                """),
                {"history_id": history_id},
            )

            record.status = StatusEnum.CANCELLED
            
            # Opsional: Jika Anda ingin menghemat kapasitas database, Anda bisa 
            # mengosongkan analysis_result. Namun jika butuh audit log, biarkan saja.
            # record.analysis_result = None 

            self.db.commit()

        except Exception as e:
            self.db.rollback()

            record.status = StatusEnum.FAILED
            record.analysis_result = {
                "error": "Gagal melakukan proses cancel finance transaction.",
                "detail": str(e),
            }

            self.db.commit()
            raise e