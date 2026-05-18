import io
import polars as pl

def process_sales_excel(raw_bytes: io.BytesIO, history_id: int) -> pl.DataFrame:
    # ==========================================
    # 0. KONFIGURASI KOLOM WAJIB
    # ==========================================
    fixed_column = [
                'SALES PERIOD MONTH', 'SALES PERIOD YEAR', 
                'JTS / MSM-I / MSM JAPAN', 'GRADE','WEEK 1',
                'WEEK 2','WEEK 3', 'WEEK 4', 'WEEK 5'
    ]
    # ==========================================
    # A. VALIDASI KOLOM
    # ==========================================
    try:
        raw_bytes.seek(0)
        df = pl.read_excel(raw_bytes, sheet_id=1)
    except Exception:
        raise ValueError("Validasi Gagal: Sheet tidak ditemukan di file Excel.")

    missing = [col for col in fixed_column if col not in df.columns]
    if missing:
        raise ValueError(f"Validasi Gagal: Kolom {missing} tidak ditemukan di Excel. Gunakan template yang benar.")
    

    try :
        df = df.with_columns(
            pl.col("WEEK 1").cast(pl.Int64, strict=False),
            pl.col("WEEK 2").cast(pl.Int64, strict=False),
            pl.col("WEEK 3").cast(pl.Int64, strict=False),
            pl.col("WEEK 4").cast(pl.Int64, strict=False),
            pl.col("WEEK 5").cast(pl.Int64, strict=False),
        )
    except Exception:
        raise ValueError("Validasi Gagal: Kolom Tidak Ditemukan.")
    

    df = df.unpivot(
        index = [
            'SALES PERIOD MONTH',
            'SALES PERIOD YEAR',
            'JTS / MSM-I / MSM JAPAN',
            'GRADE'
        ],
        value_name='value',
        variable_name='week'
    )

    df = df.drop_nulls('value')

    df.columns = ['sales_period_month', 'sales_periode_year', 'category', 'grade', 'week', 'value']


    try :
        df = df.with_columns(
            (pl.lit("01-") + pl.col("sales_period_month") + pl.lit("-") + pl.col("sales_periode_year").cast(pl.String))
            .str.to_date("%d-%B-%Y", strict=False)
            .alias("date")
        )

        df = df.drop(['sales_period_month', 'sales_periode_year'])
    except Exception as e :
        raise ValueError(f"Validasi Gagal: {e}")
    
    df = df.with_columns(
        pl.col('category').str.strip_chars()\
        .str.to_uppercase(),
        pl.col('grade').str.strip_chars()\
        .str.to_uppercase(),
        pl.col('week').str.strip_chars()\
        .str.to_uppercase(),
    )

    return df.with_columns([
        pl.lit(history_id).alias("history_id")
    ])



