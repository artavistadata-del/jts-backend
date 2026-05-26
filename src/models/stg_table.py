from typing import Optional
import datetime
import decimal
import enum

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Enum, Float, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, REAL, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from src.core.database import Base


class ActualBudgetEnum(str, enum.Enum):
    ACTUAL = 'ACTUAL'
    BUDGET = 'BUDGET'
    NA = 'NA'


class RoleEnum(str, enum.Enum):
    STAFF = 'STAFF'
    MANAGER = 'MANAGER'
    DIREKTUR = 'DIREKTUR'
    ADMIN = 'ADMIN'


class StatusActionEnum(str, enum.Enum):
    REPLACE = 'replace'
    INSERT = 'insert'


class StatusEnum(str, enum.Enum):
    ANALYZING = 'ANALYZING'
    AWAITING_PREVIEW = 'AWAITING_PREVIEW'
    PROCESSING_INSERT = 'PROCESSING_INSERT'
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'



class StagingFinanceTransactions(Base):
    __tablename__ = 'finance_transactions'
    __table_args__ = (
        ForeignKeyConstraint(['history_id'], ['oltp_main.history.id'], ondelete='CASCADE', name='fk_stg_finance_transactions_history'),
        ForeignKeyConstraint(['rule_id'], ['oltp_finance.transaction_rules.id'], name='fk_stg_finance_transactions_rule'),
        PrimaryKeyConstraint('id', name='pk_stg_finance_transactions'),
        {'schema': 'stg_table'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    history_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rule_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    period_month: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(26, 6), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    status: Mapped[Optional[StatusActionEnum]] = mapped_column(Enum(StatusActionEnum, values_callable=lambda cls: [member.value for member in cls], name='status_action_enum', schema='stg_table'))

    history: Mapped['History'] = relationship('History', back_populates='staging_finance_transactions')
    rule: Mapped['TransactionRules'] = relationship('TransactionRules', back_populates='staging_transactions')


class StagingPurchasingSheet1Transactions(Base):
    __tablename__ = 'purchasing_sheet1_transactions'
    __table_args__ = (
        ForeignKeyConstraint(['history_id'], ['oltp_main.history.id'], name='fk_purchasing_sheet1_transaction_history'),
        PrimaryKeyConstraint('id', name='pk_purchasing_sheet1_transaction'),
        {'schema': 'stg_table'}
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
    status: Mapped[Optional[StatusActionEnum]] = mapped_column(Enum(StatusActionEnum, values_callable=lambda cls: [member.value for member in cls], name='status_action_enum', schema='stg_table'))

    history: Mapped['History'] = relationship('History', back_populates='staging_purchasing_sheet1_transactions')


class StagingPurchasingSheet2Transactions(Base):
    __tablename__ = 'purchasing_sheet2_transactions'
    __table_args__ = (
        ForeignKeyConstraint(['delivery_detail_id'], ['oltp_purchasing.delivery_details.id'], name='fk_stg_purchasing_sheet2_transactions_delivery_detail'),
        ForeignKeyConstraint(['grade_id'], ['oltp_purchasing.grades.id'], name='fk_stg_purchasing_sheet2_transactions_grade'),
        ForeignKeyConstraint(['history_id'], ['oltp_main.history.id'], ondelete='CASCADE', name='fk_stg_purchasing_sheet2_transactions_history'),
        ForeignKeyConstraint(['origin_id'], ['oltp_purchasing.origins.id'], name='fk_stg_purchasing_sheet2_transactions_origin'),
        ForeignKeyConstraint(['supplier_id'], ['oltp_purchasing.suppliers.id'], name='fk_stg_purchasing_sheet2_transactions_supplier'),
        ForeignKeyConstraint(['variety_id'], ['oltp_purchasing.varieties.id'], name='fk_stg_purchasing_sheet2_transactions_variety'),
        PrimaryKeyConstraint('id', name='pk_stg_purchasing_sheet2_transactions'),
        {'schema': 'stg_table'}
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
    avg_value: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(precision=26, scale=6))
    avg_price: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(precision=26, scale=6))
    status: Mapped[Optional[StatusActionEnum]] = mapped_column(Enum(StatusActionEnum, values_callable=lambda cls: [member.value for member in cls], name='status_action_enum', schema='stg_table'))

    delivery_detail: Mapped[Optional['DeliveryDetails']] = relationship('DeliveryDetails', back_populates='staging_sheet2_transactions')
    grade: Mapped[Optional['Grades']] = relationship('Grades', back_populates='staging_sheet2_transactions')
    history: Mapped['History'] = relationship('History', back_populates='staging_purchasing_sheet2_transactions')
    origin: Mapped[Optional['Origins']] = relationship('Origins', back_populates='staging_sheet2_transactions')
    supplier: Mapped[Optional['Suppliers']] = relationship('Suppliers', back_populates='staging_sheet2_transactions')
    variety: Mapped['Varieties'] = relationship('Varieties', back_populates='staging_sheet2_transactions')


class StagingPurchasingSheet3Transactions(Base):
    __tablename__ = 'purchasing_sheet3_transactions'
    __table_args__ = (
        ForeignKeyConstraint(['history_id'], ['oltp_main.history.id'], ondelete='CASCADE', name='fk_stg_purchasing_sheet3_transactions_history'),
        ForeignKeyConstraint(['rule_id'], ['oltp_purchasing.sheet3_transaction_rules.id'], name='fk_stg_purchasing_sheet3_transactions_rule'),
        PrimaryKeyConstraint('id', name='pk_stg_purchasing_sheet3_transactions'),
        {'schema': 'stg_table'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    history_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rule_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    period_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    value: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(26, 6))
    status: Mapped[Optional[StatusActionEnum]] = mapped_column(Enum(StatusActionEnum, values_callable=lambda cls: [member.value for member in cls], name='status_action_enum', schema='stg_table'))

    history: Mapped['History'] = relationship('History', back_populates='staging_purchasing_sheet3_transactions')
    rule: Mapped['Sheet3TransactionRules'] = relationship('Sheet3TransactionRules', back_populates='staging_sheet3_transactions')


# Di dalam stg_table.py

class StagingSalesTransactions(Base):
    __tablename__ = 'sales_transactions'
    __table_args__ = (
        ForeignKeyConstraint(['history_id'], ['oltp_main.history.id'], ondelete='RESTRICT', name='fk_stg_sales_history'),
        ForeignKeyConstraint(['source_id'], ['oltp_sales.sources.id'], name='fk_stg_sales_source'),
        ForeignKeyConstraint(['product_id'], ['oltp_sales.products.id'], name='fk_stg_sales_product'),
        ForeignKeyConstraint(['grade_id'], ['oltp_sales.grades.id'], name='fk_stg_sales_grade'),
        ForeignKeyConstraint(['week_id'], ['oltp_sales.weeks.id'], name='fk_stg_sales_week'),
        PrimaryKeyConstraint('id', name='sales_transactions_pkey'),
        {'schema': 'stg_table'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    history_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    
    # Kolom relasi baru
    source_id: Mapped[int] = mapped_column(Integer, nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    
    grade_id: Mapped[int] = mapped_column(Integer, nullable=False)
    week_id: Mapped[int] = mapped_column(Integer, nullable=False)
    value: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[Optional[StatusActionEnum]] = mapped_column(Enum(StatusActionEnum, values_callable=lambda cls: [member.value for member in cls], name='status_action_enum', schema='stg_table'))

    # Definisi relationship
    history: Mapped['History'] = relationship('History', back_populates='staging_sales_transactions')
    source: Mapped['SalesSources'] = relationship('SalesSources', back_populates='staging_transactions')
    product: Mapped['SalesProducts'] = relationship('SalesProducts', back_populates='staging_transactions')
    grade: Mapped['SalesGrades'] = relationship('SalesGrades', back_populates='staging_transactions')
    week: Mapped['Weeks'] = relationship('Weeks', back_populates='staging_transactions')
