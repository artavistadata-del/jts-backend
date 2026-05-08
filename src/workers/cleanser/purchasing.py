import polars as pl
from io import BytesIO


COLUMN_MAPPING_SHEET1 = {
    "date": "price_date",

    "TEX (US No.1H/CFR Korea) + domestic cost":
        "tex_us_no_1h_cfr_korea_domestic_cost",

    "LME (USNo.1:2=80:20/CFR Turkey) + domestic cost":
        "lme_usno_1_2_80_20_cfr_turkey_domestic_cost",

    "Local ($/t)":
        "local_price_usd",

    "BUSHELING contract($/t)":
        "busheling_contract_usd",

    "PNS contract($/t)":
        "pns_contract_usd",

    "HMS contract($/t)":
        "hms_contract_usd",

    "SHR contract($/t)":
        "shr_contract_usd",

    "契約\r\nLocal (Rp)":
        "local_price_idr",

    "為替\r\n$":
        "usd_rate",

    "為替\r\n\\/Rp":
        "idr_rate",

    "為替\r\nRp/$":
        "idr_usd_exchange_rate",

    "市況（US No.1H/CFRKorea）":
        "us_no_1h_cfr_korea",

    "市況（LME USNo.1:2=80:20/CFR Turky）":
        "lme_usno_1_2_80_20_cfr_turky",

    "市況（LME USNo.1:2=80:20/CFR Turkey）":
        "lme_usno_1_2_80_20_cfr_turkey",

    "Prem. Local\r\n(Rp/kg)":
        "local_premium_idr_per_kg",
}


COLUMN_MAPPING_SHEET2 = {
    "Variety": "variety",
    "List No.": "list_no",
    "Contract Date": "contract_date",
    "Supplier": "supplier",
    "Origin": "origin",
    "ton": "ton",
    "$/tonCIF": "price_usd_per_ton_cif",
    "Total $": "total_usd",
    "Grade": "grade",
    "Delivery Detail": "delivery_detail",
    "Delivery": "delivery",
    "Actual ETA": "actual_eta",
    "Delivery Remarks": "delivery_remarks",
    "Average Qty": "avg_qty",
    "Average Value": "avg_value",
    "Average Price": "avg_price",
}


def _set_first_row_as_header(df: pl.DataFrame) -> pl.DataFrame:
    """
    Excel kamu header-nya ada di row pertama,
    bukan langsung dianggap header oleh Polars.
    """
    headers = [str(x).strip() if x is not None else "" for x in df.row(0)]
    df.columns = headers
    return df.slice(1)


def _clean_sheet1(raw_bytes: BytesIO, history_id: int) -> pl.DataFrame:
    df = pl.read_excel(
        raw_bytes,
        sheet_id=1,
        has_header=False,
        columns=list(range(16)),
    )

    df = _set_first_row_as_header(df)

    # Cast numeric berdasarkan posisi kolom setelah header dipasang
    cast_rules = {
        1: pl.Int32,
        2: pl.Float32,
        3: pl.Float32,
        4: pl.Int32,
        5: pl.Int32,
        6: pl.Int32,
        7: pl.Int32,
        8: pl.Int32,
        9: pl.Float32,
        10: pl.Int32,
        11: pl.Int32,
        12: pl.Int32,
        13: pl.Int32,
        14: pl.Float32,
        15: pl.Int32,
    }

    expressions = [
        pl.col(df.columns[idx]).cast(dtype, strict=False)
        for idx, dtype in cast_rules.items()
    ]

    df = df.with_columns(expressions)

    # Handle Date dari Excel
    if "Date" in df.columns:
        df = (
            df.with_columns(
                pl.col("Date").str.to_date("%d/%m/%Y", strict=False).alias("date")
            )
            .drop("Date")
        )
    elif "date" in df.columns:
        df = df.with_columns(
            pl.col("date").str.to_date("%d/%m/%Y", strict=False).alias("date")
        )
    else:
        raise ValueError("Sheet 1 tidak memiliki kolom Date/date.")

    df = df.rename(COLUMN_MAPPING_SHEET1)

    df = df.with_columns(
        pl.lit(history_id).cast(pl.Int32).alias("history_id")
    )

    return df


def _clean_sheet2(raw_bytes: BytesIO, history_id: int) -> pl.DataFrame:
    df = pl.read_excel(
        raw_bytes,
        sheet_id=2,
        has_header=False,
    )

    df = _set_first_row_as_header(df)
    df = df.rename(COLUMN_MAPPING_SHEET2)

    df = df.with_columns([
        pl.col("variety").cast(pl.String, strict=False),
        pl.col("list_no").cast(pl.Int32, strict=False),

        pl.col("contract_date").str.to_date("%d/%m/%Y", strict=False),
        pl.col("supplier").cast(pl.String, strict=False),
        pl.col("origin").cast(pl.String, strict=False),

        pl.col("ton").cast(pl.Int32, strict=False),
        pl.col("price_usd_per_ton_cif").cast(pl.Int32, strict=False),
        pl.col("total_usd").cast(pl.Int32, strict=False),

        pl.col("grade").cast(pl.String, strict=False),
        pl.col("delivery_detail").cast(pl.String, strict=False),

        pl.col("delivery").str.to_date("%d/%m/%Y", strict=False),
        pl.col("actual_eta").str.to_date("%d/%m/%Y", strict=False),

        # Kalau datanya bukan true/false, hasilnya bisa False/null.
        # Kalau kolom remarks sebenarnya text, ganti ke pl.String.
        (pl.col("delivery_remarks").cast(pl.String, strict=False).str.to_lowercase() == "true")
            .alias("delivery_remarks"),

        pl.col("avg_qty").cast(pl.Int32, strict=False),
        pl.col("avg_value").cast(pl.Int32, strict=False),
        pl.col("avg_price").cast(pl.Int32, strict=False),

        pl.lit(history_id).cast(pl.Int32).alias("history_id"),
    ])

    return df


def _clean_sheet3(raw_bytes: BytesIO, history_id: int) -> pl.DataFrame:
    df = pl.read_excel(
        raw_bytes,
        sheet_id=3,
        has_header=False,
    )

    df = _set_first_row_as_header(df)

    required_cols = {"Index", "Variety", "Detail"}
    missing = required_cols - set(df.columns)

    if missing:
        raise ValueError(f"Sheet 3 kolom wajib tidak ditemukan: {missing}")

    df = df.unpivot(
        index=["Index", "Variety", "Detail"],
        variable_name="date",
        value_name="value",
    )

    df = df.rename({
        "Index": "source_index",
        "Variety": "variety",
        "Detail": "detail",
    })

    df = df.with_columns([
        pl.col("source_index").cast(pl.Int32, strict=False),
        pl.col("variety").cast(pl.String, strict=False),
        pl.col("detail").cast(pl.String, strict=False),

        # Sama seperti Colab:
        # "01/2025" -> "01/01/2025" -> 2025-01-01
        (
            pl.lit("01/") + pl.col("date").cast(pl.String)
        ).str.to_date("%d/%m/%Y", strict=False).alias("price_date"),

        pl.col("value").cast(pl.Int32, strict=False),
        pl.lit(history_id).cast(pl.Int32).alias("history_id"),
    ]).drop("date")

    return df.select([
        "source_index",
        "variety",
        "detail",
        "value",
        "price_date",
        "history_id",
    ])


def process_purchasing_excel(raw_bytes: BytesIO, history_id: int) -> dict[str, pl.DataFrame]:
    """
    Return 3 dataframe karena Purchasing punya 3 sheet.
    """
    file_bytes = raw_bytes.getvalue()

    sheet1 = _clean_sheet1(BytesIO(file_bytes), history_id)
    sheet2 = _clean_sheet2(BytesIO(file_bytes), history_id)
    sheet3 = _clean_sheet3(BytesIO(file_bytes), history_id)

    return {
        "sheet1": sheet1,
        "sheet2": sheet2,
        "sheet3": sheet3,
    }