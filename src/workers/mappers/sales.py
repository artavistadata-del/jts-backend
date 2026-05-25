import polars as pl

class SalesMapper:
    @staticmethod
    def map_to_staging(df_excel: pl.DataFrame, df_rule: pl.DataFrame, history_id: int) -> pl.DataFrame:
        """
        Menggabungkan Excel Sales dengan Master Table
        """

        rule_dict = dict(zip(df_rule["master_name"], df_rule["master_id"]))

        kolom_mapping = ["source", "grade", "week", "product"]

        df_staging = df_excel.with_columns(
            [
                pl.col(kolom).replace(rule_dict, default=None).alias(f"{kolom}_id") 
                for kolom in kolom_mapping
            ]
        )
        df_staging = df_staging.drop(kolom_mapping)
        df_staging = df_staging.with_columns([
            pl.lit(history_id).alias("history_id"),
            pl.col("value").cast(pl.Int64),
            pl.col("date").cast(pl.Date)
        ])

        return df_staging