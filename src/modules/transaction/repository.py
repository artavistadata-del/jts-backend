from typing import List, Optional

from sqlalchemy.orm import Session
from src.models.models import History, StatusEnum
from src.models.stg_table import FinanceTransactions
from sqlalchemy import extract, asc, desc
from src.models.finance import Transactions, t_vw_transaction_rule_lookup
# from src.models.models import FinanceSheets, FinanceTransactionRules, FinanceTransactions

class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    # ==========================================
    # UPDATE SINGLE ROW [MANAGER ACCESS ]
    # ==========================================

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
    def get_all_finance_data(
        self, 
        skip: int, 
        limit: int, 
        report_type: str = None, 
        years: Optional[List[int]] = None,   
        months: Optional[List[int]] = None,  
        categories: Optional[List[str]] = None, # UBAH: Jadi List[str]
        search: str = None,        
        sort_by: str = "year",                  # UBAH: Default jadi year
        sort_order: str = "desc"   
    ):
        fetch_limit = limit + 1
        
        query = self.db.query(
            Transactions.id,
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
        
        # --- BLOK SEARCH & FILTER ---
        if search:
            query = query.filter(t_vw_transaction_rule_lookup.c.category_name.ilike(f"%{search}%"))
        if report_type:
            query = query.filter(t_vw_transaction_rule_lookup.c.sheet_name == report_type)
            
        if years: 
            query = query.filter(extract('year', Transactions.period_month).in_(years))
        if months: 
            query = query.filter(extract('month', Transactions.period_month).in_(months))
            
        if categories:
            query = query.filter(t_vw_transaction_rule_lookup.c.category_name.in_(categories))
        # ----------------------------

        # --- BLOK SORTING BARU ---
        # Hanya ada year, month, dan category
        sort_column_map = {
            "year": extract('year', Transactions.period_month),
            "month": extract('month', Transactions.period_month),
            "category": t_vw_transaction_rule_lookup.c.category_name
        }
        
        order_column = sort_column_map.get(sort_by, extract('year', Transactions.period_month))
        
        if sort_order.lower() == "asc":
            query = query.order_by(asc(order_column))
        else:
            query = query.order_by(desc(order_column))
        # -------------------------
            
        results = query.offset(skip).limit(fetch_limit).all()
        
        has_next = len(results) > limit
        if has_next:
            results = results[:-1]

        formatted_results = [
            {
                "id": r.id,
                "period_month": r.period_month,
                "value": float(r.amount),
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
    

    def get_finance_filter_options(self):
        """Mengambil data unik untuk dropdown filter di Frontend"""
        
        # 1. Ambil Tahun Unik
        years_query = self.db.query(
            extract('year', Transactions.period_month)
        ).distinct().order_by(
            desc(extract('year', Transactions.period_month))
        ).all()
        available_years = [int(y[0]) for y in years_query if y[0] is not None]

        # 2. Ambil Bulan Unik (Berdasarkan data yang ada di database)
        months_query = self.db.query(
            extract('month', Transactions.period_month)
        ).distinct().order_by(
            asc(extract('month', Transactions.period_month)) # Urutkan dari Jan ke Des
        ).all()
        
        # Mapping Angka ke Nama Bulan
        month_names = {
            1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
            5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
            9: "September", 10: "Oktober", 11: "November", 12: "Desember"
        }
        
        # Format ke bentuk Dictionary List (sangat disukai Frontend)
        available_months = [
            {
                "value": int(m[0]), 
                "label": month_names.get(int(m[0]), str(int(m[0]))) # Terjemahkan
            } 
            for m in months_query if m[0] is not None
        ]

        # 3. Ambil Kategori Unik
        categories_query = self.db.query(
            t_vw_transaction_rule_lookup.c.category_name
        ).distinct().order_by(
            asc(t_vw_transaction_rule_lookup.c.category_name)
        ).all()
        available_categories = [c[0] for c in categories_query if c[0] is not None]

        return {
            "years": available_years,
            "months": available_months, # TAMBAHAN
            "categories": available_categories
        }