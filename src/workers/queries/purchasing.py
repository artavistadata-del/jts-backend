from sqlalchemy import text

class PurchasingQueries:

    @staticmethod
    def get_view_data(view_name : str) :
        return text(f"""
            SELECT * from oltp_purchasing.{view_name}
        """)
    

    @staticmethod
    def insert_into_main_sheet3(stg_table : str, main_table : str) :
        return text(f"""
            INSERT INTO {main_table} (history_id, rule_id, period_date, value)
            SELECT history_id, rule_id, period_date, value
            FROM {stg_table}
            WHERE history_id = :h_id
            
            -- Jika kombinasi rule_id dan period_date ini sudah ada di main table...
            ON CONFLICT (rule_id, period_date) 
            
            DO UPDATE SET
                history_id = EXCLUDED.history_id,
                value = EXCLUDED.value
                
            WHERE {main_table}.value IS DISTINCT FROM EXCLUDED.value
        """)
        
    
    @staticmethod
    def insert_into_main_sheet2(stg_table: str, main_table: str):
        return text(f"""
            INSERT INTO {main_table} (
                history_id, variety_id, list_no, contract_date, supplier_id, origin_id, 
                grade_id, delivery_detail_id, ton, price_usd_per_ton_cif, total_usd, 
                delivery, actual_eta, delivery_remarks, avg_qty, avg_value, avg_price
            )
            SELECT 
                history_id, variety_id, list_no, contract_date, supplier_id, origin_id, 
                grade_id, delivery_detail_id, ton, price_usd_per_ton_cif, total_usd, 
                delivery, actual_eta, delivery_remarks, avg_qty, avg_value, avg_price
            FROM {stg_table}
            WHERE history_id = :h_id
            
            -- Pintu Gerbang (Unique Constraint) dari Sheet 2
            ON CONFLICT (variety_id, list_no, contract_date, supplier_id, grade_id) 
            
            DO UPDATE SET
                history_id = EXCLUDED.history_id,
                origin_id = EXCLUDED.origin_id,
                delivery_detail_id = EXCLUDED.delivery_detail_id,
                ton = EXCLUDED.ton,
                price_usd_per_ton_cif = EXCLUDED.price_usd_per_ton_cif,
                total_usd = EXCLUDED.total_usd,
                delivery = EXCLUDED.delivery,
                actual_eta = EXCLUDED.actual_eta,
                delivery_remarks = EXCLUDED.delivery_remarks,
                avg_qty = EXCLUDED.avg_qty,
                avg_value = EXCLUDED.avg_value,
                avg_price = EXCLUDED.avg_price,
                updated_at = now()
                
            -- Update hanya jika ada salah satu nilai (selain kunci unik) yang berbeda
            WHERE ROW(
                {main_table}.origin_id, {main_table}.delivery_detail_id, {main_table}.ton, 
                {main_table}.price_usd_per_ton_cif, {main_table}.total_usd, {main_table}.delivery, 
                {main_table}.actual_eta, {main_table}.delivery_remarks, {main_table}.avg_qty, 
                {main_table}.avg_value, {main_table}.avg_price
            ) IS DISTINCT FROM ROW(
                EXCLUDED.origin_id, EXCLUDED.delivery_detail_id, EXCLUDED.ton, 
                EXCLUDED.price_usd_per_ton_cif, EXCLUDED.total_usd, EXCLUDED.delivery, 
                EXCLUDED.actual_eta, EXCLUDED.delivery_remarks, EXCLUDED.avg_qty, 
                EXCLUDED.avg_value, EXCLUDED.avg_price
            )
        """)

    @staticmethod
    def insert_into_main_sheet1(stg_table: str, main_table: str):
        return text(f"""
            INSERT INTO {main_table} (
                history_id, price_date, tex_us_no_1h_cfr_korea_domestic_cost, 
                lme_usno_1_2_80_20_cfr_turkey_domestic_cost, local_price_usd, busheling_contract_usd, 
                pns_contract_usd, hms_contract_usd, shr_contract_usd, local_price_idr, usd_rate, 
                idr_rate, idr_usd_exchange_rate, us_no_1h_cfr_korea, lme_usno_1_2_80_20_cfr_turky, 
                lme_usno_1_2_80_20_cfr_turkey, local_premium_idr_per_kg
            )
            SELECT 
                history_id, price_date, tex_us_no_1h_cfr_korea_domestic_cost, 
                lme_usno_1_2_80_20_cfr_turkey_domestic_cost, local_price_usd, busheling_contract_usd, 
                pns_contract_usd, hms_contract_usd, shr_contract_usd, local_price_idr, usd_rate, 
                idr_rate, idr_usd_exchange_rate, us_no_1h_cfr_korea, lme_usno_1_2_80_20_cfr_turky, 
                lme_usno_1_2_80_20_cfr_turkey, local_premium_idr_per_kg
            FROM {stg_table}
            WHERE history_id = :h_id
            
            -- Pintu Gerbang (Unique Constraint) dari Sheet 1
            ON CONFLICT (price_date) 
            
            DO UPDATE SET
                history_id = EXCLUDED.history_id,
                tex_us_no_1h_cfr_korea_domestic_cost = EXCLUDED.tex_us_no_1h_cfr_korea_domestic_cost,
                lme_usno_1_2_80_20_cfr_turkey_domestic_cost = EXCLUDED.lme_usno_1_2_80_20_cfr_turkey_domestic_cost,
                local_price_usd = EXCLUDED.local_price_usd,
                busheling_contract_usd = EXCLUDED.busheling_contract_usd,
                pns_contract_usd = EXCLUDED.pns_contract_usd,
                hms_contract_usd = EXCLUDED.hms_contract_usd,
                shr_contract_usd = EXCLUDED.shr_contract_usd,
                local_price_idr = EXCLUDED.local_price_idr,
                usd_rate = EXCLUDED.usd_rate,
                idr_rate = EXCLUDED.idr_rate,
                idr_usd_exchange_rate = EXCLUDED.idr_usd_exchange_rate,
                us_no_1h_cfr_korea = EXCLUDED.us_no_1h_cfr_korea,
                lme_usno_1_2_80_20_cfr_turky = EXCLUDED.lme_usno_1_2_80_20_cfr_turky,
                lme_usno_1_2_80_20_cfr_turkey = EXCLUDED.lme_usno_1_2_80_20_cfr_turkey,
                local_premium_idr_per_kg = EXCLUDED.local_premium_idr_per_kg,
                updated_at = now()
                
            -- Update hanya jika ada salah satu nilai yang berbeda
            WHERE ROW(
                {main_table}.tex_us_no_1h_cfr_korea_domestic_cost, {main_table}.lme_usno_1_2_80_20_cfr_turkey_domestic_cost,
                {main_table}.local_price_usd, {main_table}.busheling_contract_usd, {main_table}.pns_contract_usd,
                {main_table}.hms_contract_usd, {main_table}.shr_contract_usd, {main_table}.local_price_idr,
                {main_table}.usd_rate, {main_table}.idr_rate, {main_table}.idr_usd_exchange_rate,
                {main_table}.us_no_1h_cfr_korea, {main_table}.lme_usno_1_2_80_20_cfr_turky, 
                {main_table}.lme_usno_1_2_80_20_cfr_turkey, {main_table}.local_premium_idr_per_kg
            ) IS DISTINCT FROM ROW(
                EXCLUDED.tex_us_no_1h_cfr_korea_domestic_cost, EXCLUDED.lme_usno_1_2_80_20_cfr_turkey_domestic_cost,
                EXCLUDED.local_price_usd, EXCLUDED.busheling_contract_usd, EXCLUDED.pns_contract_usd,
                EXCLUDED.hms_contract_usd, EXCLUDED.shr_contract_usd, EXCLUDED.local_price_idr,
                EXCLUDED.usd_rate, EXCLUDED.idr_rate, EXCLUDED.idr_usd_exchange_rate,
                EXCLUDED.us_no_1h_cfr_korea, EXCLUDED.lme_usno_1_2_80_20_cfr_turky, 
                EXCLUDED.lme_usno_1_2_80_20_cfr_turkey, EXCLUDED.local_premium_idr_per_kg
            )
        """)
    

    @staticmethod
    def update_staging_status_sheet3(stg_table: str, main_table: str):
        return text(f"""
            UPDATE {stg_table} stg
            SET status = CASE
                -- 👇 PERBAIKAN: Tambahkan casting ::stg_table.status_action_enum
                WHEN m.rule_id IS NULL THEN 'insert'::stg_table.status_action_enum
                WHEN m.value IS DISTINCT FROM stg.value THEN 'replace'::stg_table.status_action_enum
                ELSE NULL
            END
            FROM {stg_table} s
            LEFT JOIN {main_table} m 
                ON s.rule_id = m.rule_id 
                AND s.period_date = m.period_date -- Business Key Sheet 3
            WHERE stg.id = s.id 
              AND stg.history_id = :h_id;
        """)

    @staticmethod
    def update_staging_status_sheet2(stg_table: str, main_table: str):
        return text(f"""
            UPDATE {stg_table} stg
            SET status = CASE
                -- 👇 PERBAIKAN: Tambahkan casting ::stg_table.status_action_enum
                WHEN m.variety_id IS NULL THEN 'insert'::stg_table.status_action_enum
                WHEN ROW(
                    m.origin_id, m.delivery_detail_id, m.ton, m.price_usd_per_ton_cif, 
                    m.total_usd, m.delivery, m.actual_eta, m.delivery_remarks, 
                    m.avg_qty, m.avg_value, m.avg_price
                ) IS DISTINCT FROM ROW(
                    stg.origin_id, stg.delivery_detail_id, stg.ton, stg.price_usd_per_ton_cif, 
                    stg.total_usd, stg.delivery, stg.actual_eta, stg.delivery_remarks, 
                    stg.avg_qty, stg.avg_value, stg.avg_price
                ) THEN 'replace'::stg_table.status_action_enum
                ELSE NULL
            END
            FROM {stg_table} s
            LEFT JOIN {main_table} m 
                ON s.variety_id = m.variety_id 
                AND s.list_no = m.list_no 
                AND s.contract_date = m.contract_date 
                AND s.supplier_id = m.supplier_id 
                AND s.grade_id = m.grade_id -- Business Key Sheet 2
            WHERE stg.id = s.id 
              AND stg.history_id = :h_id;
        """)

    @staticmethod
    def update_staging_status_sheet1(stg_table: str, main_table: str):
        return text(f"""
            UPDATE {stg_table} stg
            SET status = CASE
                -- 👇 PERBAIKAN: Tambahkan casting ::stg_table.status_action_enum
                WHEN m.price_date IS NULL THEN 'insert'::stg_table.status_action_enum
                WHEN ROW(
                    m.tex_us_no_1h_cfr_korea_domestic_cost, m.lme_usno_1_2_80_20_cfr_turkey_domestic_cost,
                    m.local_price_usd, m.busheling_contract_usd, m.pns_contract_usd,
                    m.hms_contract_usd, m.shr_contract_usd, m.local_price_idr,
                    m.usd_rate, m.idr_rate, m.idr_usd_exchange_rate,
                    m.us_no_1h_cfr_korea, m.lme_usno_1_2_80_20_cfr_turky, 
                    m.lme_usno_1_2_80_20_cfr_turkey, m.local_premium_idr_per_kg
                ) IS DISTINCT FROM ROW(
                    stg.tex_us_no_1h_cfr_korea_domestic_cost, stg.lme_usno_1_2_80_20_cfr_turkey_domestic_cost,
                    stg.local_price_usd, stg.busheling_contract_usd, stg.pns_contract_usd,
                    stg.hms_contract_usd, stg.shr_contract_usd, stg.local_price_idr,
                    stg.usd_rate, stg.idr_rate, stg.idr_usd_exchange_rate,
                    stg.us_no_1h_cfr_korea, stg.lme_usno_1_2_80_20_cfr_turky, 
                    stg.lme_usno_1_2_80_20_cfr_turkey, stg.local_premium_idr_per_kg
                ) THEN 'replace'::stg_table.status_action_enum
                ELSE NULL
            END
            FROM {stg_table} s
            LEFT JOIN {main_table} m 
                ON s.price_date = m.price_date -- Business Key Sheet 1
            WHERE stg.id = s.id 
              AND stg.history_id = :h_id;
        """)