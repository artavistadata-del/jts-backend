from sqlalchemy.orm import Session
from src.models.models import History, StatusEnum
from src.models.stg_table import FinanceTransactions
from src.models.finance import Transactions, t_vw_transaction_rule_lookup
# from src.models.models import FinanceSheets, FinanceTransactionRules, FinanceTransactions

class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    # ==========================================
    # GET transaction [MANAGER & USER ACCESS ]
    # ==========================================
    def get_paginated_transactions(self, model_class, skip: int, limit: int, user_id_filter: int = None, report_type: str = None):
        # 1. Join tabel Fact (contoh: FactFinance) dengan History
        query = self.db.query(model_class).join(
            History, model_class.history_id == History.id
        )

        # 2. Jika ada nik_filter (berarti dia Staff), saring datanya
        if user_id_filter:
            query = query.filter(History.user_id == user_id_filter)

        # 3. Saring berdasarkan report_type (IS / BS) jika parameter dikirim
        # Gunakan hasattr untuk mencegah error pada model departemen lain yang mungkin tidak punya kolom report_type
        if report_type and hasattr(model_class, 'report_type'):
            query = query.filter(model_class.report_type == report_type)

        # 4. Hitung total untuk pagination
        total_count = query.count()

        # 5. Ambil data dengan offset & limit
        results = query.order_by(model_class.id.desc())\
                       .offset(skip)\
                       .limit(limit)\
                       .all()
                       
        return results, total_count

    # ==========================================
    # UPDATE SINGLE ROW [MANAGER ACCESS ]
    # ==========================================
    def update_single_row(self, model_class, id_fact: int, new_value: float, manager_nik: str):
        # Cari data berdasarkan ID tabel fact yang dilempar
        row = self.db.query(model_class).get(id_fact)
        
        if not row:
            raise ValueError("Data tidak ditemukan di database.")
            
        # Pengecekan relasi ke History (harus PENDING)
        if row.history.status != StatusEnum.PENDING:
            raise ValueError("Hanya data berstatus PENDING yang bisa dikoreksi.")

        # # Logic Audit Trail
        # if not row.is_edited:
        #     row.original_value = row.value # Simpan data asli Excel
            
        row.value = new_value
        # row.is_edited = True
        # row.edited_by = manager_nik
        
        self.db.commit()
        return row

    # ==========================================
    # GET ALL PURCHASING TRANSACTIONS (NO COUNT)
    # ==========================================
    def get_all_purchasing_data(self, model_class, skip: int, limit: int):
        
        fetch_limit = limit + 1
        
        results = (
            self.db.query(model_class)
            .order_by(model_class.id.desc())
            .offset(skip)
            .limit(fetch_limit)
            .all()
        )
        
        has_next = len(results) > limit
        
        if has_next:
            results = results[:-1]
            
        return results, has_next


    # ==========================================
    # GET ALL FINANCE TRANSACTIONS (NO SELECT *)
    # ==========================================
    # def get_all_finance_data(self, skip: int, limit: int, report_type: str = None):
    
    #     fetch_limit = limit + 1
        
    #     query = self.db.query(
    #         FinanceTransactions.id,
    #         FinanceTransactions.history_id,
    #         FinanceTransactions.rule_id,
    #         FinanceTransactions.period_month,
    #         FinanceTransactions.amount,
    #         t_vw_finance_transaction_rule_lookup.c.sheet_name,
    #         t_vw_finance_transaction_rule_lookup.c.category_name,
    #         t_vw_finance_transaction_rule_lookup.c.sub_category_name,
    #         t_vw_finance_transaction_rule_lookup.c.sub_sub_category_name,
    #         t_vw_finance_transaction_rule_lookup.c.account_name,
    #         t_vw_finance_transaction_rule_lookup.c.actual_budget
    #     ).join(
    #         t_vw_finance_transaction_rule_lookup, 
    #         FinanceTransactions.rule_id == t_vw_finance_transaction_rule_lookup.c.rule_id
    #     )
        
    #     if report_type:
    #         query = query.filter(
    #             t_vw_finance_transaction_rule_lookup.c.sheet_name == report_type
    #         )
            
    #     results = (
    #         query.order_by(FinanceTransactions.id.desc())
    #         .offset(skip)
    #         .limit(fetch_limit)
    #         .all()
    #     )
        
    #     has_next = len(results) > limit
        
    #     if has_next:
    #         results = results[:-1]

    #     # 4. FORMAT HASIL KE DICTIONARY
    #     # Semua deskripsi huruf sekarang akan ikut terkirim ke frontend
    #     formatted_results = [
    #         {
    #             # "id": r.id,
    #             # "history_id": r.history_id,
    #             # "rule_id": r.rule_id,
    #             "period_month": r.period_month,
    #             "amount": float(r.amount),
    #             "sheet_name": r.sheet_name,
    #             "category_name": r.category_name,
    #             "sub_category_name": r.sub_category_name,
    #             "sub_sub_category_name": r.sub_sub_category_name,
    #             "account_name": r.account_name,
    #             "actual_budget": r.actual_budget,
    #             # "last_modified" : r.updated_at
    #         }
    #         for r in results
    #     ]
            
    #     return formatted_results, has_next



    def get_all_finance_data(self, skip: int, limit: int, report_type: str = None):
        
        fetch_limit = limit + 1
        
        # PENYESUAIAN: Menggunakan 'Transactions' dan 't_vw_transaction_rule_lookup'
        query = self.db.query(
            Transactions.id,
            Transactions.history_id,
            Transactions.rule_id,
            Transactions.period_month,
            Transactions.amount,
            t_vw_transaction_rule_lookup.c.sheet_name,
            t_vw_transaction_rule_lookup.c.category_name,
            t_vw_transaction_rule_lookup.c.sub_category_name,
            t_vw_transaction_rule_lookup.c.sub_sub_category_name,
            t_vw_transaction_rule_lookup.c.account_name,
            t_vw_transaction_rule_lookup.c.actual_budget
        ).join(
            t_vw_transaction_rule_lookup, 
            Transactions.rule_id == t_vw_transaction_rule_lookup.c.rule_id
        )
        
        if report_type:
            query = query.filter(
                t_vw_transaction_rule_lookup.c.sheet_name == report_type
            )
            
        results = (
            query.order_by(Transactions.id.desc())
            .offset(skip)
            .limit(fetch_limit)
            .all()
        )
        
        has_next = len(results) > limit
        
        if has_next:
            results = results[:-1]

        # 4. FORMAT HASIL KE DICTIONARY
        formatted_results = [
            {
                "id": r.id,
                # "history_id": r.history_id,
                # "rule_id": r.rule_id,
                "period_month": r.period_month,
                "value": float(r.amount),
                "sheet_name": r.sheet_name,
                "category_name": r.category_name,
                "sub_category_name": r.sub_category_name,
                "sub_sub_category_name": r.sub_sub_category_name,
                "account_name": r.account_name,
                "actual_budget": r.actual_budget,
                # "last_modified" : r.updated_at
            }
            for r in results
        ]
            
        return formatted_results, has_next
    


    # Di dalam class Repository Anda
    def update_finance_transaction(self, transaction_id: int, new_amount: float):
        # 1. Cari datanya dulu
        transaction = self.db.query(Transactions).filter(Transactions.id == transaction_id).first()
        
        if not transaction:
            return None # Return None jika ID tidak ditemukan
            
        # 2. Update nilainya
        transaction.amount = new_amount
        
        # 3. Commit perubahan
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction

    def delete_finance_transaction(self, transaction_id: int):
        # 1. Cari datanya
        transaction = self.db.query(Transactions).filter(Transactions.id == transaction_id).first()
        
        if not transaction:
            return False # Return False jika ID tidak ditemukan
            
        # 2. Hapus datanya
        self.db.delete(transaction)
        self.db.commit()
        
        return True
    

    def get_staging_finance_data(self, history_id: int, skip: int, limit: int, report_type: str = None):
        fetch_limit = limit + 1
        
        query = self.db.query(
            FinanceTransactions.id,
            FinanceTransactions.history_id,
            FinanceTransactions.rule_id,
            FinanceTransactions.period_month,
            FinanceTransactions.amount,
            FinanceTransactions.status,  
            t_vw_transaction_rule_lookup.c.sheet_name,
            t_vw_transaction_rule_lookup.c.category_name,
            t_vw_transaction_rule_lookup.c.sub_category_name,
            t_vw_transaction_rule_lookup.c.sub_sub_category_name,
            t_vw_transaction_rule_lookup.c.account_name,
            t_vw_transaction_rule_lookup.c.actual_budget
        ).join(
            t_vw_transaction_rule_lookup, 
            FinanceTransactions.rule_id == t_vw_transaction_rule_lookup.c.rule_id
        ).filter(
            FinanceTransactions.status.isnot(None),
            # TAMBAHAN KUNCI: Filter berdasarkan history_id
            FinanceTransactions.history_id == history_id
        )
        
        if report_type:
            query = query.filter(
                t_vw_transaction_rule_lookup.c.sheet_name == report_type
            )
            
        results = (
            query.order_by(FinanceTransactions.id.desc())
            .offset(skip)
            .limit(fetch_limit)
            .all()
        )
        
        has_next = len(results) > limit
        if has_next:
            results = results[:-1]

        formatted_results = [
            {
                "id": r.id,
                # "history_id": r.history_id,
                "period_month": r.period_month,
                "value": float(r.amount),
                "status": r.status.value if r.status else None,
                "sheet_name": r.sheet_name,
                "category_name": r.category_name,
                "sub_category_name": r.sub_category_name,
                "sub_sub_category_name": r.sub_sub_category_name,
                "account_name": r.account_name,
                "actual_budget": r.actual_budget,
            }
            for r in results
        ]
            
        return formatted_results, has_next

    def wipe_all_finance_transactions(self) -> int:
        """MENGHAPUS SELURUH ISI TABEL TRANSAKSI!"""
        deleted_count = self.db.query(Transactions).delete(synchronize_session=False)
        
        self.db.commit()
        return deleted_count