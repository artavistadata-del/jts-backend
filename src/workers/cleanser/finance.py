import io
import polars as pl

def process_finance_excel(raw_bytes: io.BytesIO, history_id: int) -> list[dict]:
    # ==========================================
    # Validasi File Excel
    # ==========================================
    df_bs = pl.read_excel(raw_bytes, sheet_name='BS', has_header=True)

    fixed_column_bs = [
        'Idx Category', 'Category', 'Idx Sub Category', 
        'Sub Category', 'Sub Sub Category', 'Account Name'
        ]

    fixed_column_is = [
        'Idx Category','Category', 'Idx Sub Category', 'Sub Category', 'Account Name', 'Actual/Budget'
        ]

    # --- A. Validasi Sheet BS ---
    try:
        raw_bytes.seek(0)
        df_bs = pl.read_excel(raw_bytes, sheet_name='BS', has_header=True)
    except Exception:
        raise ValueError("Validasi Gagal: Sheet 'BS' (Balance Sheet) tidak ditemukan di file Excel.")

    # Cek apakah ada kolom wajib yang hilang di BS
    missing_bs = [col for col in fixed_column_bs if col not in df_bs.columns]
    if missing_bs:
        raise ValueError(f"Validasi Gagal: Kolom {missing_bs} tidak ditemukan di Sheet 'BS'. Gunakan template yang benar.")

    # --- B. Validasi Sheet IS ---
    try:
        raw_bytes.seek(0)
        df_is = pl.read_excel(raw_bytes, sheet_name='IS', has_header=True)
    except Exception:
        raise ValueError("Validasi Gagal: Sheet 'IS' (Income Statement) tidak ditemukan di file Excel.")

    # Cek apakah ada kolom wajib yang hilang di IS
    missing_is = [col for col in fixed_column_is if col not in df_is.columns]
    if missing_is:
        raise ValueError(f"Validasi Gagal: Kolom {missing_is} tidak ditemukan di Sheet 'IS'. Gunakan template yang benar.")
    
    # ==========================================
    # 1. PROSES SHEET "BS" (Balance Sheet)
    # ==========================================
    df_bs_long = df_bs.unpivot(
    index=fixed_column_bs,
    variable_name="bulan",
    value_name="value"
    )

    df_bs_clean = df_bs_long.with_columns([
    pl.lit("BS").alias("report_type"),
    pl.lit(None).alias("Actual/Budget").cast(pl.Utf8),
    pl.col('Idx Category').cast(pl.Utf8),     
    pl.col('Idx Sub Category').cast(pl.Utf8), 
    pl.col('value').cast(pl.Float64, strict=False).fill_null(0.0),
    ("01/" + pl.col("bulan")).str.to_date("%d/%m/%Y").alias("bulan")
    ])

    # ==========================================
    # 2. PROSES SHEET "IS" (Income Statement)
    # ==========================================
    raw_bytes.seek(0) 

    df_is = pl.read_excel(raw_bytes, sheet_name='IS', has_header=True)

    
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
    ("01/" + pl.col("bulan")).str.to_date("%d/%m/%Y").alias("bulan")
    ])

    df_is_clean = df_is_clean.select(df_bs_clean.columns)


    df_final = pl.concat([df_bs_clean, df_is_clean])

    new_columns = [col.lower().replace(" ", "_").replace("/", "_") for col in df_final.columns]
    df_final.columns = new_columns

    df_final = df_final.with_columns([
        pl.lit(history_id).alias("id_history")
    ])

    return df_final

