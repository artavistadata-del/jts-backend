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

class FinanceMapper:
    
    @staticmethod
    def prepare_rule_lookup(df_rule: pl.DataFrame, join_cols: list) -> pl.DataFrame:
        """Membersihkan DataFrame Rule dan mengecek duplikasi master."""
        if df_rule.height == 0:
            raise ValueError("Rule lookup kosong. Pastikan master finance_transaction_rules sudah diisi.")

        df_rule = df_rule.with_columns([
            normalize_key_expr("sheet_name").alias("sheet_name"),
            normalize_key_expr("category_name").alias("category_name"),
            normalize_key_expr("sub_category_name").alias("sub_category_name"),
            normalize_key_expr("sub_sub_category_name").alias("sub_sub_category_name"),
            normalize_key_expr("account_name").alias("account_name"),
            normalize_key_expr("actual_budget").alias("actual_budget"),
            pl.col("rule_id").cast(pl.Int64),
        ])

        # Validasi Duplikat Rule
        duplicate_rule = df_rule.group_by(join_cols).agg(pl.len().alias("total")).filter(pl.col("total") > 1)
        if duplicate_rule.height > 0:
            raise ValueError(f"Rule lookup memiliki kombinasi duplicate. Contoh: {duplicate_rule.head(10).to_dicts()}")

        return df_rule

    @staticmethod
    def map_to_staging(df_excel: pl.DataFrame, df_rule: pl.DataFrame, join_cols: list, history_id: int) -> pl.DataFrame:
        """Mapping data Excel yang sudah dicuci ke Master Rule"""
        
        # 1. Rename Kolom Excel
        rename_map = {
            "sheet_type": "sheet_name",
            "category": "category_name",
            "sub_category": "sub_category_name",
            "sub_sub_category": "sub_sub_category_name",
        }
        df_excel = df_excel.rename({old: new for old, new in rename_map.items() if old in df_excel.columns})

        # 2. Validasi Kolom Wajib
        required_cols = join_cols + ["period_month", "amount"]
        missing_cols = [c for c in required_cols if c not in df_excel.columns]
        if missing_cols:
            raise ValueError(f"Kolom hasil cleansing belum lengkap: {missing_cols}")

        # 3. Normalisasi Data Excel
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

        # 4. Validasi Data Null
        invalid_month = df_excel.filter(pl.col("period_month").is_null())
        if invalid_month.height > 0:
            raise ValueError(f"Ada period_month kosong/gagal parse. Contoh: {invalid_month.head(10).to_dicts()}")

        invalid_amount = df_excel.filter(pl.col("amount").is_null())
        if invalid_amount.height > 0:
            raise ValueError(f"Ada amount kosong/gagal parse. Contoh: {invalid_amount.head(10).to_dicts()}")

        # 5. Join dengan Rule
        df_mapped = df_excel.join(
            df_rule.select(join_cols + ["rule_id"]),
            on=join_cols,
            how="left",
        )

        # 6. Cek Rule Tidak Ditemukan
        invalid_rule = df_mapped.filter(pl.col("rule_id").is_null()).select(join_cols).unique()
        if invalid_rule.height > 0:
            raise ValueError(f"Ada kombinasi rule belum terdaftar. Contoh: {invalid_rule.head(50).to_dicts()}")

        # 7. Cek Duplikat di File Excel
        duplicate_upload = df_mapped.group_by(["rule_id", "period_month"]).agg(pl.len().alias("total")).filter(pl.col("total") > 1)
        if duplicate_upload.height > 0:
            raise ValueError(f"File upload memiliki duplicate pada kombinasi rule_id + period_month. Contoh: {duplicate_upload.head(20).to_dicts()}")

        # 8. Filter Kolom Final untuk Staging
        df_staging = df_mapped.select([
            pl.lit(history_id).cast(pl.Int64).alias("history_id"),
            pl.col("rule_id").cast(pl.Int64),
            pl.col("period_month"),
            pl.col("amount"),
        ])


        return df_staging