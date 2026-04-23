from sqlalchemy.orm import Session
from fastapi import Depends
from models.models.models import FactFinance

class FinanceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id_fact: int) -> FactFinance | None:
        return self.db.query(FactFinance).filter(FactFinance.id_fact == id_fact).first()

    def update(self, db_obj: FactFinance, update_data: dict) -> FactFinance:
        for key, value in update_data.items():
            setattr(db_obj, key, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def select_all_finance_paginated(self, skip: int, limit: int):
        total_data = self.db.query(FactFinance).count()
        
        finances = (
            self.db.query(FactFinance)
            .order_by(FactFinance.id_fact.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return total_data, finances