# from sqlalchemy import text

# class FinanceQueries:
    
#     @staticmethod
#     def get_rule_lookup(view_name: str):
#         return text(f"""
#             SELECT
#                 rule_id, sheet_name, category_name, sub_category_name,
#                 sub_sub_category_name, account_name, actual_budget
#             FROM {view_name}
#         """)

#     @staticmethod
#     def get_preview_insert(stg_table: str, main_table: str):
#         return text(f"""
#             SELECT s.*
#             FROM {stg_table} s
#             LEFT JOIN {main_table} f
#                 ON s.rule_id = f.rule_id
#                AND s.period_month = f.period_month
#             WHERE s.history_id = :history_id
#               AND f.id IS NULL
#         """)

#     @staticmethod
#     def get_preview_replace(stg_table: str, main_table: str):
#         return text(f"""
#             SELECT
#                 s.*,
#                 f.amount AS old_amount
#             FROM {stg_table} s
#             JOIN {main_table} f
#                 ON s.rule_id = f.rule_id
#                AND s.period_month = f.period_month
#             WHERE s.history_id = :history_id
#               AND s.amount IS DISTINCT FROM f.amount
#         """)

#     @staticmethod
#     def get_wip_mismatch(stg_table: str, main_table: str, rule_lookup_view: str):
#         return text(f"""
#             WITH StagingBeginning AS (
#                 SELECT s.period_month, s.amount
#                 FROM {stg_table} s
#                 JOIN {rule_lookup_view} r ON s.rule_id = r.rule_id
#                 WHERE s.history_id = :history_id
#                 AND r.account_name = 'WIP BEGINNING BALANCE'
#                 AND r.actual_budget = 'ACTUAL'
#             ),
#             StagingEnding AS (
#                 SELECT s.period_month, s.amount
#                 FROM {stg_table} s
#                 JOIN {rule_lookup_view} r ON s.rule_id = r.rule_id
#                 WHERE s.history_id = :history_id
#                 AND r.account_name = 'WIP ENDING BALANCE'
#                 AND r.actual_budget = 'ACTUAL'
#             ),
#             MainEnding AS (
#                 SELECT f.period_month, f.amount
#                 FROM {main_table} f
#                 JOIN {rule_lookup_view} r ON f.rule_id = r.rule_id
#                 WHERE r.account_name = 'WIP ENDING BALANCE'
#                 AND r.actual_budget = 'ACTUAL'
#                 AND NOT EXISTS (
#                     SELECT 1 FROM StagingEnding se
#                     WHERE se.period_month = f.period_month
#                 )
#             ),
#             EndingCombined AS (
#                 SELECT period_month, amount FROM StagingEnding
#                 UNION ALL
#                 SELECT period_month, amount FROM MainEnding
#             )
#             SELECT
#                 sb.period_month AS bulan_upload,
#                 sb.amount AS nilai_beginning_baru,
#                 ec.amount AS nilai_ending_lama
#             FROM StagingBeginning sb
#             LEFT JOIN EndingCombined ec
#                 ON ec.period_month = (sb.period_month - INTERVAL '1 month')::DATE
#             WHERE
#                 ec.amount IS NULL
#                 OR ROUND(ABS(sb.amount)::numeric, 6) IS DISTINCT FROM ROUND(ABS(ec.amount)::numeric, 6)
#         """)

#     @staticmethod
#     def insert_into_main(stg_table: str, main_table: str):
#         return text(f"""
#             INSERT INTO {main_table} (history_id, rule_id, period_month, amount)
#             SELECT history_id, rule_id, period_month, amount
#             FROM {stg_table}
#             WHERE history_id = :history_id
            
#             ON CONFLICT (rule_id, period_month)
            
#             DO UPDATE SET
#                 history_id = EXCLUDED.history_id,
#                 amount = EXCLUDED.amount,
#                 updated_at = now()
                
#             WHERE {main_table}.amount IS DISTINCT FROM EXCLUDED.amount
#                OR {main_table}.history_id IS DISTINCT FROM EXCLUDED.history_id
#         """)


from sqlalchemy import text

class FinanceQueries:
    
    @staticmethod
    def get_rule_lookup(view_name: str):
        """
        Mengambil data lookup rule untuk validasi nama akun dan kategori.
        """
        return text(f"""
            SELECT
                rule_id, sheet_name, category_name, sub_category_name,
                sub_sub_category_name, account_name, actual_budget
            FROM {view_name}
        """)

    @staticmethod
    def update_staging_status(stg_table: str, main_table: str):
        """
        Menandai kolom 'status' di tabel staging secara fisik.
        Langkah wajib sebelum memanggil preview maupun insert_into_main.
        """
        return text(f"""
            -- 1. Tandai data yang berstatus 'insert' (belum ada di main table)
            UPDATE {stg_table} s
            SET status = 'insert'
            WHERE s.history_id = :history_id
              AND NOT EXISTS (
                  SELECT 1 FROM {main_table} f
                  WHERE s.rule_id = f.rule_id AND s.period_month = f.period_month
              );

            -- 2. Tandai data yang berstatus 'replace' (sudah ada di main table tapi nominalnya berubah)
            UPDATE {stg_table} s
            SET status = 'replace'
            FROM {main_table} f
            WHERE s.history_id = :history_id
              AND s.rule_id = f.rule_id
              AND s.period_month = f.period_month
              AND s.amount IS DISTINCT FROM f.amount;
        """)

    @staticmethod
    def get_preview_insert(stg_table: str, main_table: str):
        """
        Mengambil data dari staging yang siap di-insert sebagai data baru.
        """
        return text(f"""
            SELECT s.*
            FROM {stg_table} s
            WHERE s.history_id = :history_id
              AND s.status = 'insert'
        """)

    @staticmethod
    def get_preview_replace(stg_table: str, main_table: str):
        """
        Mengambil data dari staging yang akan menimpa data lama beserta nilai lamanya (old_amount).
        """
        return text(f"""
            SELECT 
                s.*,
                f.amount AS old_amount
            FROM {stg_table} s
            JOIN {main_table} f
                ON s.rule_id = f.rule_id
               AND s.period_month = f.period_month
            WHERE s.history_id = :history_id
              AND s.status = 'replace'
        """)

    @staticmethod
    def get_wip_mismatch(stg_table: str, main_table: str, rule_lookup_view: str):
        """
        Validasi akuntansi untuk mengecek apakah Beginning Balance bulan ini
        sesuai dengan Ending Balance bulan lalu.
        """
        return text(f"""
            WITH StagingBeginning AS (
                SELECT s.period_month, s.amount
                FROM {stg_table} s
                JOIN {rule_lookup_view} r ON s.rule_id = r.rule_id
                WHERE s.history_id = :history_id
                AND r.account_name = 'WIP BEGINNING BALANCE'
                AND r.actual_budget = 'ACTUAL'
            ),
            StagingEnding AS (
                SELECT s.period_month, s.amount
                FROM {stg_table} s
                JOIN {rule_lookup_view} r ON s.rule_id = r.rule_id
                WHERE s.history_id = :history_id
                AND r.account_name = 'WIP ENDING BALANCE'
                AND r.actual_budget = 'ACTUAL'
            ),
            MainEnding AS (
                SELECT f.period_month, f.amount
                FROM {main_table} f
                JOIN {rule_lookup_view} r ON f.rule_id = r.rule_id
                WHERE r.account_name = 'WIP ENDING BALANCE'
                AND r.actual_budget = 'ACTUAL'
                AND NOT EXISTS (
                    SELECT 1 FROM StagingEnding se
                    WHERE se.period_month = f.period_month
                )
            ),
            EndingCombined AS (
                SELECT period_month, amount FROM StagingEnding
                UNION ALL
                SELECT period_month, amount FROM MainEnding
            )
            SELECT
                sb.period_month AS bulan_upload,
                sb.amount AS nilai_beginning_baru,
                ec.amount AS nilai_ending_lama
            FROM StagingBeginning sb
            LEFT JOIN EndingCombined ec
                ON ec.period_month = (sb.period_month - INTERVAL '1 month')::DATE
            WHERE
                ec.amount IS NULL
                OR ROUND(ABS(sb.amount)::numeric, 6) IS DISTINCT FROM ROUND(ABS(ec.amount)::numeric, 6)
        """)

    @staticmethod
    def insert_into_main(stg_table: str, main_table: str):
        """
        Proses Upsert super ringan. Hanya memproses baris data yang statusnya 
        sudah ditandai sebagai 'insert' atau 'replace' saja.
        """
        return text(f"""
            INSERT INTO {main_table} (history_id, rule_id, period_month, amount)
            SELECT 
                history_id, 
                rule_id, 
                period_month, 
                amount
            FROM {stg_table}
            WHERE history_id = :history_id
              AND status IN ('insert', 'replace')
            
            ON CONFLICT (rule_id, period_month)
            
            DO UPDATE SET
                history_id = EXCLUDED.history_id,
                amount = EXCLUDED.amount,
                updated_at = now()
                
            WHERE {main_table}.amount IS DISTINCT FROM EXCLUDED.amount
               OR {main_table}.history_id IS DISTINCT FROM EXCLUDED.history_id
        """)