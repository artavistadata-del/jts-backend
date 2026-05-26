from decimal import Decimal
import decimal
from typing import Optional
import datetime
import enum

from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, Enum, Float, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, REAL, String, Table, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from src.core.database import Base


class DeliveryDetails(Base):
    __tablename__ = 'delivery_details'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_purchasing_delivery_details'),
        UniqueConstraint('name', name='uq_purchasing_delivery_details_name'),
        {'schema': 'oltp_purchasing'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    sheet2_transactions: Mapped[list['PurchasingSheet2Transactions']] = relationship('PurchasingSheet2Transactions', back_populates='delivery_detail')
    # 👇 TAMBAHKAN BARIS INI
    staging_sheet2_transactions: Mapped[list['StagingPurchasingSheet2Transactions']] = relationship('StagingPurchasingSheet2Transactions', back_populates='delivery_detail')


class Details(Base):
    __tablename__ = 'details'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_purchasing_details'),
        UniqueConstraint('name', name='uq_purchasing_details_name'),
        {'schema': 'oltp_purchasing'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    sheet3_transaction_rules: Mapped[list['Sheet3TransactionRules']] = relationship('Sheet3TransactionRules', back_populates='detail')


class Grades(Base):
    __tablename__ = 'grades'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_purchasing_grades'),
        UniqueConstraint('name', name='uq_purchasing_grades_name'),
        {'schema': 'oltp_purchasing'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    sheet2_transactions: Mapped[list['PurchasingSheet2Transactions']] = relationship('PurchasingSheet2Transactions', back_populates='grade')
    # 👇 TAMBAHKAN BARIS INI
    staging_sheet2_transactions: Mapped[list['StagingPurchasingSheet2Transactions']] = relationship('StagingPurchasingSheet2Transactions', back_populates='grade')


class Origins(Base):
    __tablename__ = 'origins'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_purchasing_origins'),
        UniqueConstraint('name', name='uq_purchasing_origins_name'),
        {'schema': 'oltp_purchasing'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    sheet2_transactions: Mapped[list['PurchasingSheet2Transactions']] = relationship('PurchasingSheet2Transactions', back_populates='origin')
    # 👇 TAMBAHKAN BARIS INI
    staging_sheet2_transactions: Mapped[list['StagingPurchasingSheet2Transactions']] = relationship('StagingPurchasingSheet2Transactions', back_populates='origin')

class Suppliers(Base):
    __tablename__ = 'suppliers'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_purchasing_suppliers'),
        UniqueConstraint('name', name='uq_purchasing_suppliers_name'),
        {'schema': 'oltp_purchasing'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    sheet2_transactions: Mapped[list['PurchasingSheet2Transactions']] = relationship('PurchasingSheet2Transactions', back_populates='supplier')
    # 👇 TAMBAHKAN BARIS INI
    staging_sheet2_transactions: Mapped[list['StagingPurchasingSheet2Transactions']] = relationship('StagingPurchasingSheet2Transactions', back_populates='supplier')


class Varieties(Base):
    __tablename__ = 'varieties'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_purchasing_varieties'),
        UniqueConstraint('name', name='uq_purchasing_varieties_name'),
        {'schema': 'oltp_purchasing'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    sheet3_transaction_rules: Mapped[list['Sheet3TransactionRules']] = relationship('Sheet3TransactionRules', back_populates='variety')
    sheet2_transactions: Mapped[list['PurchasingSheet2Transactions']] = relationship('PurchasingSheet2Transactions', back_populates='variety')
    # 👇 TAMBAHKAN BARIS INI
    staging_sheet2_transactions: Mapped[list['StagingPurchasingSheet2Transactions']] = relationship('StagingPurchasingSheet2Transactions', back_populates='variety')

t_vw_sheet2_master = Table(
    'vw_sheet2_master', Base.metadata,
    Column('master_type', Text),
    Column('master_id', BigInteger),
    Column('master_name', Text),
    schema='oltp_purchasing'
)


t_vw_sheet3_rules = Table(
    'vw_sheet3_rules', Base.metadata,
    Column('rule_id', BigInteger),
    Column('detail', Text),
    Column('variety', Text),
    schema='oltp_purchasing'
)




class Sheet3TransactionRules(Base):
    __tablename__ = 'sheet3_transaction_rules'
    __table_args__ = (
        ForeignKeyConstraint(['detail_id'], ['oltp_purchasing.details.id'], name='fk_purchasing_sheet3_rules_detail'),
        ForeignKeyConstraint(['variety_id'], ['oltp_purchasing.varieties.id'], name='fk_purchasing_sheet3_rules_variety'),
        PrimaryKeyConstraint('id', name='pk_purchasing_sheet3_transaction_rules'),
        UniqueConstraint('variety_id', 'detail_id', name='uq_purchasing_sheet3_rules_combo'),
        {'schema': 'oltp_purchasing'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    variety_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    detail_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    detail: Mapped['Details'] = relationship('Details', back_populates='sheet3_transaction_rules')
    variety: Mapped['Varieties'] = relationship('Varieties', back_populates='sheet3_transaction_rules')
    sheet3_transactions: Mapped[list['PurchasingSheet3Transactions']] = relationship('PurchasingSheet3Transactions', back_populates='rule')
    # 👇 TAMBAHKAN BARIS INI
    staging_sheet3_transactions: Mapped[list['StagingPurchasingSheet3Transactions']] = relationship('StagingPurchasingSheet3Transactions', back_populates='rule')


class PurchasingSheet1Transactions(Base):
    __tablename__ = 'sheet1_transactions'
    __table_args__ = (
        ForeignKeyConstraint(['history_id'], ['oltp_main.history.id'], name='fk_purchasing_sheet1_transaction_history'),
        PrimaryKeyConstraint('id', name='pk_purchasing_sheet1_transaction'),
        UniqueConstraint('price_date', name='uq_purchasing_sheet1_transaction_price_date'),
        {'schema': 'oltp_purchasing'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    history_id: Mapped[int] = mapped_column(Integer, nullable=False)
    price_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    tex_us_no_1h_cfr_korea_domestic_cost: Mapped[Optional[int]] = mapped_column(Integer)
    lme_usno_1_2_80_20_cfr_turkey_domestic_cost: Mapped[Optional[float]] = mapped_column(REAL)
    local_price_usd: Mapped[Optional[float]] = mapped_column(REAL)
    busheling_contract_usd: Mapped[Optional[int]] = mapped_column(Integer)
    pns_contract_usd: Mapped[Optional[int]] = mapped_column(Integer)
    hms_contract_usd: Mapped[Optional[int]] = mapped_column(Integer)
    shr_contract_usd: Mapped[Optional[int]] = mapped_column(Integer)
    local_price_idr: Mapped[Optional[int]] = mapped_column(Integer)
    usd_rate: Mapped[Optional[float]] = mapped_column(REAL)
    idr_rate: Mapped[Optional[int]] = mapped_column(Integer)
    idr_usd_exchange_rate: Mapped[Optional[int]] = mapped_column(Integer)
    us_no_1h_cfr_korea: Mapped[Optional[int]] = mapped_column(Integer)
    lme_usno_1_2_80_20_cfr_turky: Mapped[Optional[int]] = mapped_column(Integer)
    lme_usno_1_2_80_20_cfr_turkey: Mapped[Optional[float]] = mapped_column(REAL)
    local_premium_idr_per_kg: Mapped[Optional[int]] = mapped_column(Integer)

    history: Mapped['History'] = relationship('History', back_populates='purchasing_sheet1_transactions')


class PurchasingSheet2Transactions(Base):
    __tablename__ = 'sheet2_transactions'
    __table_args__ = (
        ForeignKeyConstraint(['delivery_detail_id'], ['oltp_purchasing.delivery_details.id'], name='fk_purchasing_sheet2_transactions_delivery_detail'),
        ForeignKeyConstraint(['grade_id'], ['oltp_purchasing.grades.id'], name='fk_purchasing_sheet2_transactions_grade'),
        ForeignKeyConstraint(['history_id'], ['oltp_main.history.id'], name='fk_purchasing_sheet2_transactions_history'),
        ForeignKeyConstraint(['origin_id'], ['oltp_purchasing.origins.id'], name='fk_purchasing_sheet2_transactions_origin'),
        ForeignKeyConstraint(['supplier_id'], ['oltp_purchasing.suppliers.id'], name='fk_purchasing_sheet2_transactions_supplier'),
        ForeignKeyConstraint(['variety_id'], ['oltp_purchasing.varieties.id'], name='fk_purchasing_sheet2_transactions_variety'),
        PrimaryKeyConstraint('id', name='pk_purchasing_sheet2_transactions'),
        UniqueConstraint('variety_id', 'list_no', 'contract_date', 'supplier_id', 'grade_id', name='uq_purchasing_sheet2_transactions_business_key'),
        {'schema': 'oltp_purchasing'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    history_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    variety_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    list_no: Mapped[Optional[int]] = mapped_column(Integer)
    contract_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    supplier_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    origin_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    grade_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    delivery_detail_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    ton: Mapped[Optional[int]] = mapped_column(BigInteger)
    price_usd_per_ton_cif: Mapped[Optional[int]] = mapped_column(BigInteger)
    total_usd: Mapped[Optional[int]] = mapped_column(BigInteger)
    delivery: Mapped[Optional[datetime.date]] = mapped_column(Date)
    actual_eta: Mapped[Optional[datetime.date]] = mapped_column(Date)
    delivery_remarks: Mapped[Optional[str]] = mapped_column(Text)
    avg_qty: Mapped[Optional[float]] = mapped_column(Float)
    avg_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=26, scale=6))
    avg_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=26, scale=6))

    delivery_detail: Mapped[Optional['DeliveryDetails']] = relationship('DeliveryDetails', back_populates='sheet2_transactions')
    grade: Mapped[Optional['Grades']] = relationship('Grades', back_populates='sheet2_transactions')
    history: Mapped['History'] = relationship('History', back_populates='purchasing_sheet2_transactions')
    origin: Mapped[Optional['Origins']] = relationship('Origins', back_populates='sheet2_transactions')
    supplier: Mapped[Optional['Suppliers']] = relationship('Suppliers', back_populates='sheet2_transactions')
    variety: Mapped['Varieties'] = relationship('Varieties', back_populates='sheet2_transactions')


class PurchasingSheet3Transactions(Base):
    __tablename__ = 'sheet3_transactions'
    __table_args__ = (
        ForeignKeyConstraint(['history_id'], ['oltp_main.history.id'], name='fk_purchasing_sheet3_transactions_history'),
        ForeignKeyConstraint(['rule_id'], ['oltp_purchasing.sheet3_transaction_rules.id'], name='fk_purchasing_sheet3_transactions_rule'),
        PrimaryKeyConstraint('id', name='pk_purchasing_sheet3_transactions'),
        UniqueConstraint('rule_id', 'period_date', name='uq_purchasing_sheet3_transactions_rule_period'),
        {'schema': 'oltp_purchasing'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    history_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rule_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    period_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    value: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(26, 6))

    history: Mapped['History'] = relationship('History', back_populates='purchasing_sheet3_transactions')
    rule: Mapped['Sheet3TransactionRules'] = relationship('Sheet3TransactionRules', back_populates='sheet3_transactions')
