import polars as pl
from io import BytesIO

class FinanceBSService:
    @staticmethod
    def process_balance_sheet(file_bytes: bytes) -> list[dict]:
        file_buffer = BytesIO(file_bytes)

        # ✅ 1. BACA EXCEL TANPA xlsx2csv (INI KUNCI)
        df = pl.read_excel(
            file_buffer,
            sheet_name="BS",
            read_options={"has_header": False}
        )

        # ✅ 2. Paksa nama kolom generik
        df.columns = [f"COL_{i}" for i in range(len(df.columns))]

        # ✅ 3. Cari baris header ("NO")
        start_index = 0
        for i in range(min(10, df.height)):
            row = [str(x).strip().upper() for x in df.row(i) if x is not None]
            if "NO" in row:
                start_index = i
                break

        # ✅ 4. Potong sampai header
        df = df.slice(start_index)

        # ✅ 5. Ambil header
        raw_headers = [
            str(x).strip().upper().replace("\u00A0", " ")
            if x is not None else f"UNKNOWN_{i}"
            for i, x in enumerate(df.row(0))
        ]

        # Hindari duplikat
        headers = []
        for i, h in enumerate(raw_headers):
            if h in headers or h == "":
                headers.append(f"UNKNOWN_{i}")
            else:
                headers.append(h)

        df = df.rename(dict(zip(df.columns, headers))).slice(1)

        categories = [
            {"prefix": "3.1", "cat": "LIABILITIES AND EQUITY", "sub": "EQUITY", "sub_sub": "-"},
            {"prefix": "2.1", "cat": "LIABILITIES AND EQUITY", "sub": "LIABILITY", "sub_sub": "CURRENT LIABILITIES"},
            {"prefix": "2.2", "cat": "LIABILITIES AND EQUITY", "sub": "LIABILITY", "sub_sub": "NON CURRENT LIABILITY"},
            {"prefix": "1.1", "cat": "ASSETS", "sub": "CURRENT ASSETS", "sub_sub": "-"},
            {"prefix": "1.2", "cat": "ASSETS", "sub": "NON CURRENT ASSETS", "sub_sub": "-"},
        ]

        results = []
        for cfg in categories:
            out = FinanceBSService._process_section(
                df,
                cfg["prefix"],
                cfg["cat"],
                cfg["sub"],
                cfg["sub_sub"]
            )
            if out is not None and out.height > 0:
                results.append(out)
        print (results)
        if not results:
            return []

        return pl.concat(results).to_dicts()

    @staticmethod
    def _process_section(
        df: pl.DataFrame,
        prefix: str,
        category: str,
        sub_category: str,
        sub_sub_category: str
    ) -> pl.DataFrame | None:

        print("==== SAMPLE NO VALUES ====")
        print(
            df
            .select(pl.col("NO"))
            .head(20)
        )


        print(
            df
            .select(pl.col("NO").cast(pl.Utf8))
            .head(20)
        )

        
        normalized_no = (
            pl.col("NO")
            .cast(pl.Utf8)
            .str.replace_all("\u00a0", "")
            .str.replace_all(" ", "")
        )

        section_df = df.filter(
            normalized_no.is_not_null() &
            normalized_no.str.contains(f"^{prefix}")
        )


        if section_df.is_empty():
            return None

        # ✅ MELT (API COMPATIBLE)
        section_df = section_df.melt(
            id_vars=["NO", "ACCOUNT NAME"],
            variable_name="Attribute",
            value_name="Value"
        )

        # ✅ TRANSFORMASI
        section_df = (
            section_df
            .rename({"NO": "No", "ACCOUNT NAME": "Account Name"})
            .with_columns([
                pl.lit(category).alias("Category"),
                pl.lit(sub_category).alias("Sub Category"),
                pl.lit(sub_sub_category).alias("Sub Sub Category"),

                # ✅ FORMAT TANGGAL SESUAI EXCEL
                pl.col("Attribute")
                  .str.strptime(pl.Date, "%d/%m/%Y", strict=False)
                  .cast(pl.Utf8)
                  .alias("Date"),

                pl.col("Value").cast(pl.Float64, strict=False),
            ])
            .drop_nulls(subset=["Date"])
            .with_columns(
                pl.concat_str(
                    [pl.col("No"), pl.col("Account Name")],
                    separator=" "
                ).alias("Account Name")
            )
            .select([
                "Category",
                "Sub Category",
                "Sub Sub Category",
                "Account Name",
                "Date",
                "Value"
            ])
        )

        return section_df
