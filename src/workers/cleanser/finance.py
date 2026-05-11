import io
import polars as pl

def process_finance_excel(raw_bytes: io.BytesIO, history_id: int) -> pl.DataFrame:
    # ==========================================
    # 0. KONFIGURASI KOLOM WAJIB
    # ==========================================
    fixed_column_bs = [
        'Idx Category', 'Category', 'Idx Sub Category', 
        'Sub Category', 'Sub Sub Category', 'Account Name'
    ]

    fixed_column_is = [
        'Idx Category','Category', 'Idx Sub Category', 
        'Sub Category', 'Account Name', 'Actual/Budget'
    ]

    # ==========================================
    # A. VALIDASI & LOAD SHEET "BS"
    # ==========================================
    try:
        raw_bytes.seek(0)
        df_bs = pl.read_excel(raw_bytes, sheet_name='BS', has_header=True)
    except Exception:
        raise ValueError("Validasi Gagal: Sheet 'BS' (Balance Sheet) tidak ditemukan di file Excel.")

    missing_bs = [col for col in fixed_column_bs if col not in df_bs.columns]
    if missing_bs:
        raise ValueError(f"Validasi Gagal: Kolom {missing_bs} tidak ditemukan di Sheet 'BS'. Gunakan template yang benar.")

    # ==========================================
    # B. VALIDASI & LOAD SHEET "IS"
    # ==========================================
    try:
        raw_bytes.seek(0)
        df_is = pl.read_excel(raw_bytes, sheet_name='IS', has_header=True)
    except Exception:
        raise ValueError("Validasi Gagal: Sheet 'IS' (Income Statement) tidak ditemukan di file Excel.")

    missing_is = [col for col in fixed_column_is if col not in df_is.columns]
    if missing_is:
        raise ValueError(f"Validasi Gagal: Kolom {missing_is} tidak ditemukan di Sheet 'IS'. Gunakan template yang benar.")

    # ==========================================
    # 1. PROSES SHEET "BS" (Balance Sheet)
    # ==========================================
    # Langsung gunakan df_bs yang sudah berhasil di-load di atas
    df_bs_long = df_bs.unpivot(
        index=fixed_column_bs,
        variable_name="period_month",
        value_name="amount"
    )

    df_bs_clean = df_bs_long.with_columns([
        pl.lit("BS").alias("sheet_type"),
        pl.lit(None).alias("Actual/Budget").cast(pl.Utf8),
        pl.col('Idx Category').cast(pl.Utf8),    
        pl.col('Idx Sub Category').cast(pl.Utf8), 
        pl.col('amount').cast(pl.Float64, strict=False).fill_null(0.0),
        ("01/" + pl.col("period_month")).str.to_date("%d/%m/%Y").alias("period_month")
    ])

    # ==========================================
    # 2. PROSES SHEET "IS" (Income Statement)
    # ==========================================
    # Langsung gunakan df_is yang sudah berhasil di-load di atas
    df_is_long = df_is.unpivot(
        index=fixed_column_is,
        variable_name="period_month", 
        value_name="amount"
    )

    df_is_clean = df_is_long.with_columns([
        pl.lit("IS").alias("sheet_type"),
        pl.lit(None).alias("Sub Sub Category").cast(pl.Utf8),
        pl.col('Idx Category').cast(pl.Utf8),    
        pl.col('Idx Sub Category').cast(pl.Utf8), 
        pl.col('amount').cast(pl.Float64, strict=False).fill_null(0.0),
        ("01/" + pl.col("period_month")).str.to_date("%d/%m/%Y").alias("period_month")
    ])

    # Samakan urutan kolom IS dengan BS
    df_is_clean = df_is_clean.select(df_bs_clean.columns)

    # ==========================================
    # 3. GABUNGKAN DAN RAPIMAN KOLOM
    # ==========================================
    df_final = pl.concat([df_bs_clean, df_is_clean])

    new_columns = [col.lower().replace(" ", "_").replace("/", "_") for col in df_final.columns]
    df_final.columns = new_columns

    df_final = df_final.with_columns([
        pl.lit(history_id).alias("history_id")
    ])

    # =========================================================================
    # 4. SOLUSI CARDINALITY VIOLATION: TANGANI DUPLIKAT (PENTING!)
    # =========================================================================

    df_final = df_final.with_columns(
        pl.col("account_name")
        .str.replace_all(r"[\d.]", "")
        .str.strip_chars()
        .str.to_uppercase(),
        pl.col("sub_sub_category").replace("-", "NO SUB SUB CATEGORY").fill_null("NO SUB SUB CATEGORY"),
        pl.col('actual_budget').str.to_uppercase().fill_null("NA")
    )

    df_final = df_final.drop(['idx_category', 'idx_sub_category'])

    return df_final


