import io
import polars as pl

def process_finance_excel(raw_bytes: io.BytesIO, history_id: int) -> list[dict]:

    # ==========================================
    # 1. PROSES SHEET "BS" (Balance Sheet)
    # ==========================================
    df_bs = pl.read_excel(raw_bytes, sheet_name='BS', has_header=False)
    df_bs.columns = df_bs.row(0)
    df_bs = df_bs.slice(1)
    
    fixed_column_bs = [
        'Idx Category', 'Category', 'Idx Sub Category', 
        'Sub Category', 'Sub Sub Category', 'Account Name'
    ]
    df_bs_long = df_bs.unpivot(
        index=fixed_column_bs,
        variable_name="bulan",
        value_name="value"
    )
    
    df_bs_clean = df_bs_long.with_columns([
        pl.lit("BS").alias("report_type"),
        pl.col('Idx Category').cast(pl.Utf8),     
        pl.col('Idx Sub Category').cast(pl.Utf8), 
        pl.col('value').cast(pl.Float64, strict=False).fill_null(0.0),
        pl.col('bulan').str.to_datetime().cast(pl.Date)
    ])

    # ==========================================
    # 2. PROSES SHEET "IS" (Income Statement)
    # ==========================================
    raw_bytes.seek(0) 

    df_is = pl.read_excel(raw_bytes, sheet_name='IS', has_header=False)
    df_is.columns = df_is.row(0)
    df_is = df_is.slice(1)
    
    fixed_column_is = [
        'Idx Category','Category', 'Idx Sub Category', 'Sub Category', 'Account Name'
    ]
    df_is_long = df_is.unpivot(
        index=fixed_column_is,
        variable_name="bulan", 
        value_name="value"
    )
    
    df_is_clean = df_is_long.with_columns([
        pl.lit("IS").alias("report_type"),
        pl.lit(None).alias("Sub Sub Category").cast(pl.Utf8),
        pl.col('Idx Category').cast(pl.Utf8),     
        pl.col('Idx Sub Category').cast(pl.Utf8), 
        pl.col('value').cast(pl.Float64, strict=False).fill_null(0.0),
        pl.col('bulan').str.to_datetime().cast(pl.Date)
    ])

    df_is_clean = df_is_clean.select(df_bs_clean.columns)
    
    df_final = pl.concat([df_bs_clean, df_is_clean])

    new_columns = [col.lower().replace(" ", "_") for col in df_final.columns]
    df_final.columns = new_columns

    df_final = df_final.with_columns([
        pl.lit(history_id).alias("id_history")
    ])

    return df_final