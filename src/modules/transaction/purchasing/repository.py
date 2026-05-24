from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.models.stg_table import StagingPurchasingSheet1Transactions, StagingPurchasingSheet2Transactions, StagingPurchasingSheet3Transactions
from src.modules.transaction.purchasing.models import (
    PurchasingSheet1Transactions,
    PurchasingSheet2Transactions,
    PurchasingSheet3Transactions,
    DeliveryDetails, Grades, Origins, Suppliers, Varieties, Details, Sheet3TransactionRules
)

class PurchasingTransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_purchasing_data(
        self, 
        sheet_type: str, 
        skip: int, 
        limit: int
    ) -> Tuple[list, bool]:
        
        fetch_limit = limit + 1
        formatted_results = []
        has_next = False

        # ==========================================
        # LOGIKA SHEET 1 (FULL OPTIMIZED)
        # ==========================================
        if sheet_type == "sheet1":
            # Hanya tarik kolom yang diperlukan, jangan panggil ORM class utuh
            query = self.db.query(
                PurchasingSheet1Transactions.id,
                PurchasingSheet1Transactions.price_date,
                PurchasingSheet1Transactions.local_price_usd,
                PurchasingSheet1Transactions.busheling_contract_usd,
                PurchasingSheet1Transactions.pns_contract_usd,
                PurchasingSheet1Transactions.hms_contract_usd,
                PurchasingSheet1Transactions.shr_contract_usd,
                PurchasingSheet1Transactions.local_price_idr,
                PurchasingSheet1Transactions.usd_rate,
                PurchasingSheet1Transactions.idr_rate,
            ).order_by(desc(PurchasingSheet1Transactions.price_date))
            
            results = query.offset(skip).limit(fetch_limit).all()
            has_next = len(results) > limit
            if has_next: results = results[:-1]

            # Hasilnya berupa tuple, bisa dipanggil seperti array index atau dot notation (r.id)
            for r in results:
                formatted_results.append({
                    "id": r.id,
                    "price_date": r.price_date,
                    "local_price_usd": float(r.local_price_usd) if r.local_price_usd else None,
                    "busheling_contract_usd": r.busheling_contract_usd,
                    "pns_contract_usd": r.pns_contract_usd,
                    "hms_contract_usd": r.hms_contract_usd,
                    "shr_contract_usd": r.shr_contract_usd,
                    "local_price_idr": r.local_price_idr,
                    "usd_rate": float(r.usd_rate) if r.usd_rate else None,
                    "idr_rate": r.idr_rate,
                })

        # ==========================================
        # LOGIKA SHEET 2 (FULL OPTIMIZED)
        # ==========================================
        elif sheet_type == "sheet2":
            query = self.db.query(
                # Tarik spesifik kolom transaksi
                PurchasingSheet2Transactions.id,
                PurchasingSheet2Transactions.contract_date,
                PurchasingSheet2Transactions.list_no,
                PurchasingSheet2Transactions.ton,
                PurchasingSheet2Transactions.price_usd_per_ton_cif,
                PurchasingSheet2Transactions.total_usd,
                PurchasingSheet2Transactions.delivery,
                PurchasingSheet2Transactions.actual_eta,
                # Tarik spesifik nama master
                DeliveryDetails.name.label("delivery_detail_name"),
                Grades.name.label("grade_name"),
                Origins.name.label("origin_name"),
                Suppliers.name.label("supplier_name"),
                Varieties.name.label("variety_name")
            ).outerjoin(DeliveryDetails, PurchasingSheet2Transactions.delivery_detail_id == DeliveryDetails.id) \
             .outerjoin(Grades, PurchasingSheet2Transactions.grade_id == Grades.id) \
             .outerjoin(Origins, PurchasingSheet2Transactions.origin_id == Origins.id) \
             .outerjoin(Suppliers, PurchasingSheet2Transactions.supplier_id == Suppliers.id) \
             .outerjoin(Varieties, PurchasingSheet2Transactions.variety_id == Varieties.id) \
             .order_by(desc(PurchasingSheet2Transactions.contract_date))

            results = query.offset(skip).limit(fetch_limit).all()
            has_next = len(results) > limit
            if has_next: results = results[:-1]

            for row in results:
                formatted_results.append({
                    "id": row.id,
                    "contract_date": row.contract_date,
                    "list_no": row.list_no,
                    "supplier_name": row.supplier_name,
                    "variety_name": row.variety_name,
                    "origin_name": row.origin_name,
                    "grade_name": row.grade_name,
                    "delivery_detail_name": row.delivery_detail_name,
                    "ton": row.ton,
                    "price_usd_per_ton_cif": row.price_usd_per_ton_cif,
                    "total_usd": row.total_usd,
                    "delivery": row.delivery,
                    "actual_eta": row.actual_eta,
                })

        # ==========================================
        # LOGIKA SHEET 3 (FULL OPTIMIZED)
        # ==========================================
        elif sheet_type == "sheet3":
            query = self.db.query(
                PurchasingSheet3Transactions.id,
                PurchasingSheet3Transactions.period_date,
                PurchasingSheet3Transactions.value,
                Varieties.name.label("variety_name"),
                Details.name.label("detail_name")
            ).join(Sheet3TransactionRules, PurchasingSheet3Transactions.rule_id == Sheet3TransactionRules.id) \
             .join(Varieties, Sheet3TransactionRules.variety_id == Varieties.id) \
             .join(Details, Sheet3TransactionRules.detail_id == Details.id) \
             .order_by(desc(PurchasingSheet3Transactions.period_date))

            results = query.offset(skip).limit(fetch_limit).all()
            has_next = len(results) > limit
            if has_next: results = results[:-1]

            for row in results:
                formatted_results.append({
                    "id": row.id,
                    "period_date": row.period_date,
                    "variety_name": row.variety_name,
                    "detail_name": row.detail_name,
                    "value": float(row.value) if row.value is not None else None,
                })

        return formatted_results, has_next
    

    # ==========================================
    # GET STAGING (HANYA INSERT & REPLACE)
    # ==========================================
    def get_staging_purchasing_data(
        self, sheet_type: str, history_id: int, skip: int, limit: int
    ) -> Tuple[list, bool]:
        
        fetch_limit = limit + 1
        formatted_results = []
        has_next = False

        # --- LOGIKA STAGING SHEET 1 ---
        if sheet_type == "sheet1":
            model = StagingPurchasingSheet1Transactions
            query = self.db.query(
                model.id, model.status, model.price_date, model.local_price_usd,
                model.busheling_contract_usd, model.pns_contract_usd,
                model.hms_contract_usd, model.shr_contract_usd,
                model.local_price_idr, model.usd_rate, model.idr_rate
            ).filter(
                model.history_id == history_id,
                model.status.isnot(None) # 👈 FILTER: Abaikan status NULL (data yang tidak berubah)
            ).order_by(desc(model.id))
            
            results = query.offset(skip).limit(fetch_limit).all()
            has_next = len(results) > limit
            if has_next: results = results[:-1]

            for r in results:
                formatted_results.append({
                    "id": r.id,
                    "status": r.status.value if r.status else None,
                    "price_date": r.price_date,
                    "local_price_usd": float(r.local_price_usd) if r.local_price_usd else None,
                    "busheling_contract_usd": r.busheling_contract_usd,
                    "pns_contract_usd": r.pns_contract_usd,
                    "hms_contract_usd": r.hms_contract_usd,
                    "shr_contract_usd": r.shr_contract_usd,
                    "local_price_idr": r.local_price_idr,
                    "usd_rate": float(r.usd_rate) if r.usd_rate else None,
                    "idr_rate": r.idr_rate,
                })

        # --- LOGIKA STAGING SHEET 2 ---
        elif sheet_type == "sheet2":
            model = StagingPurchasingSheet2Transactions
            query = self.db.query(
                model.id, model.status, model.contract_date, model.list_no,
                model.ton, model.price_usd_per_ton_cif, model.total_usd,
                model.delivery, model.actual_eta, model.delivery_remarks,
                DeliveryDetails.name.label("delivery_detail_name"),
                Grades.name.label("grade_name"),
                Origins.name.label("origin_name"),
                Suppliers.name.label("supplier_name"),
                Varieties.name.label("variety_name")
            ).outerjoin(DeliveryDetails, model.delivery_detail_id == DeliveryDetails.id) \
             .outerjoin(Grades, model.grade_id == Grades.id) \
             .outerjoin(Origins, model.origin_id == Origins.id) \
             .outerjoin(Suppliers, model.supplier_id == Suppliers.id) \
             .outerjoin(Varieties, model.variety_id == Varieties.id) \
             .filter(
                 model.history_id == history_id,
                 model.status.isnot(None) # 👈 FILTER
             ).order_by(desc(model.id))

            results = query.offset(skip).limit(fetch_limit).all()
            has_next = len(results) > limit
            if has_next: results = results[:-1]

            for row in results:
                formatted_results.append({
                    "id": row.id,
                    "status": row.status.value if row.status else None,
                    "contract_date": row.contract_date,
                    "list_no": row.list_no,
                    "supplier_name": row.supplier_name,
                    "variety_name": row.variety_name,
                    "origin_name": row.origin_name,
                    "grade_name": row.grade_name,
                    "delivery_detail_name": row.delivery_detail_name,
                    "ton": row.ton,
                    "price_usd_per_ton_cif": row.price_usd_per_ton_cif,
                    "total_usd": row.total_usd,
                    "delivery": row.delivery,
                    "actual_eta": row.actual_eta,
                    "delivery_remarks": row.delivery_remarks
                })

        # --- LOGIKA STAGING SHEET 3 ---
        elif sheet_type == "sheet3":
            model = StagingPurchasingSheet3Transactions
            query = self.db.query(
                model.id, model.status, model.period_date, model.value,
                Varieties.name.label("variety_name"),
                Details.name.label("detail_name")
            ).join(Sheet3TransactionRules, model.rule_id == Sheet3TransactionRules.id) \
             .join(Varieties, Sheet3TransactionRules.variety_id == Varieties.id) \
             .join(Details, Sheet3TransactionRules.detail_id == Details.id) \
             .filter(
                 model.history_id == history_id,
                 model.status.isnot(None) # 👈 FILTER
             ).order_by(desc(model.id))

            results = query.offset(skip).limit(fetch_limit).all()
            has_next = len(results) > limit
            if has_next: results = results[:-1]

            for row in results:
                formatted_results.append({
                    "id": row.id,
                    "status": row.status.value if row.status else None,
                    "period_date": row.period_date,
                    "variety_name": row.variety_name,
                    "detail_name": row.detail_name,
                    "value": float(row.value) if row.value is not None else None,
                })

        return formatted_results, has_next