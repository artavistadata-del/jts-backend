import polars as pl

class PurchasingMapper:
    @staticmethod
    def map_sheet3_to_staging(df_excel: pl.DataFrame, df_rule: pl.DataFrame, history_id: int) -> pl.DataFrame:
        """
        Menggabungkan Excel Purchasing dengan Rule.
        """
        # 1. Rapikan nama kolom Excel agar mudah di-join
        df_excel = df_excel.rename({
            col: col.strip().lower().replace(" ", "_") 
            for col in df_excel.columns
        })

        # 2. Gabungkan Excel dengan Rule (Misal berdasarkan nama detail & variety)
        df_staging = df_excel.join(
            df_rule,
            left_on=["detail", "variety"],  # Kolom di Excel
            right_on=["detail", "variety"], # Kolom di Database (View)
            how="inner"
        )

        # 3. Tambahkan kolom history_id dan tanggal
        df_staging = df_staging.with_columns([
            pl.lit(history_id).alias("history_id"),
            pl.col("value").cast(pl.Int64), # Pastikan value berupa angka
            pl.col("period_date").cast(pl.Date)
        ])

        # 4. Pilih hanya kolom yang mau dimasukkan ke tabel database
        df_staging = df_staging.select([
            "history_id",
            "rule_id",     # Berasal dari df_rule (View)
            "period_date",
            "value"
        ])

        return df_staging
    

    @staticmethod
    def map_sheet2_to_staging(df_excel: pl.DataFrame, df_rule: pl.DataFrame, history_id: int) -> pl.DataFrame:

        """
        Menggabungkan Excel Purchasing dengan Rule.
        """

        rule_dict = dict(zip(df_rule["master_name"], df_rule["master_id"]))

        kolom_mapping = ["variety", "supplier", "origin", "grade", "delivery_detail"]

        df_staging = df_excel.with_columns(
            [
                pl.col(kolom).replace(rule_dict, default=None).alias(f"{kolom}_id") 
                for kolom in kolom_mapping
            ]
        )

        df_staging = df_staging.drop(kolom_mapping)

        df_staging = df_staging.with_columns([
            pl.lit(history_id).alias("history_id")
        ])

        return df_staging