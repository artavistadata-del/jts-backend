from sqlalchemy import text

class SalesQueries:

    @staticmethod
    def get_view_data(view_name : str) :
        return text(f"""
            SELECT * from oltp_sales.{view_name}
        """)
    

    @staticmethod
    def insert_into_main(stg_table : str, main_table : str) :
        return text(f"""
            INSERT INTO {main_table} (history_id, date, source_id, grade_id, week_id, product_id, value)
            SELECT history_id, date, source_id, grade_id, week_id, product_id, value
            FROM {stg_table}
            WHERE history_id = :h_id

            ON CONFLICT (date, source_id, grade_id, week_id, product_id) 

            DO UPDATE SET
                history_id = EXCLUDED.history_id,
                value = EXCLUDED.value
                
            WHERE {main_table}.value IS DISTINCT FROM EXCLUDED.value
            OR {main_table}.history_id IS DISTINCT FROM EXCLUDED.history_id;
        """)