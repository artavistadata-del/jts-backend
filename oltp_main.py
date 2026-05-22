from typing import Optional
import datetime
import decimal
import enum

from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, Double, Enum, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, REAL, Sequence, String, Table, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# class Base(DeclarativeBase):
#     pass

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


class StatusEnum(str, enum.Enum):
    ANALYZING = 'ANALYZING'
    AWAITING_PREVIEW = 'AWAITING_PREVIEW'
    PROCESSING_INSERT = 'PROCESSING_INSERT'
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'


class Departments(Base):
    __tablename__ = 'departments'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='departments_pkey'),
        Index('ix_departments_public_id', 'public_id', unique=True),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(Integer, Sequence('departments_id_dept_seq', schema='oltp_main'), primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(45))
    public_id: Mapped[Optional[str]] = mapped_column(String(22))

    users: Mapped[list['Users']] = relationship('Users', back_populates='department')
    history: Mapped[list['History']] = relationship('History', back_populates='department')


class FinanceAccountNames(Base):
    __tablename__ = 'finance_account_names'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_finance_account_names'),
        UniqueConstraint('account_name', name='uq_finance_account_names_account_name'),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    account_name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    finance_transaction_rules: Mapped[list['FinanceTransactionRules']] = relationship('FinanceTransactionRules', back_populates='account_name')


class FinanceCategories(Base):
    __tablename__ = 'finance_categories'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_finance_categories'),
        UniqueConstraint('name', name='uq_finance_categories_name'),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    finance_transaction_rules: Mapped[list['FinanceTransactionRules']] = relationship('FinanceTransactionRules', back_populates='category')


class FinanceSheets(Base):
    __tablename__ = 'finance_sheets'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_finance_sheets'),
        UniqueConstraint('name', name='uq_finance_sheets_name'),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    finance_transaction_rules: Mapped[list['FinanceTransactionRules']] = relationship('FinanceTransactionRules', back_populates='sheet')


class FinanceSubCategories(Base):
    __tablename__ = 'finance_sub_categories'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_finance_sub_categories'),
        UniqueConstraint('name', name='uq_finance_sub_categories_name'),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    finance_transaction_rules: Mapped[list['FinanceTransactionRules']] = relationship('FinanceTransactionRules', back_populates='sub_category')


class FinanceSubSubCategories(Base):
    __tablename__ = 'finance_sub_sub_categories'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_finance_sub_sub_categories'),
        UniqueConstraint('name', name='uq_finance_sub_sub_categories_name'),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    is_placeholder: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    finance_transaction_rules: Mapped[list['FinanceTransactionRules']] = relationship('FinanceTransactionRules', back_populates='sub_sub_category')


class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='roles_pkey'),
        Index('ix_roles_public_id', 'public_id', unique=True),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(Integer, Sequence('roles_id_roles_seq', schema='oltp_main'), primary_key=True)
    name: Mapped[Optional[RoleEnum]] = mapped_column(Enum(RoleEnum, values_callable=lambda cls: [member.value for member in cls], name='role_enum', schema='oltp_main'))
    public_id: Mapped[Optional[str]] = mapped_column(String(22))

    users: Mapped[list['Users']] = relationship('Users', back_populates='role')
    history: Mapped[list['History']] = relationship('History', back_populates='role')


t_vw_finance_transaction_rule_lookup = Table(
    'vw_finance_transaction_rule_lookup', Base.metadata,
    Column('rule_id', BigInteger),
    Column('sheet_name', Text),
    Column('category_name', Text),
    Column('sub_category_name', Text),
    Column('sub_sub_category_name', Text),
    Column('account_name', Text),
    Column('actual_budget', Text),
    Column('is_active', Boolean),
    schema='oltp_main'
)


class FinanceTransactionRules(Base):
    __tablename__ = 'finance_transaction_rules'
    __table_args__ = (
        ForeignKeyConstraint(['account_name_id'], ['oltp_main.finance_account_names.id'], name='fk_finance_transaction_rules_account_name'),
        ForeignKeyConstraint(['category_id'], ['oltp_main.finance_categories.id'], name='fk_finance_transaction_rules_category'),
        ForeignKeyConstraint(['sheet_id'], ['oltp_main.finance_sheets.id'], name='fk_finance_transaction_rules_sheet'),
        ForeignKeyConstraint(['sub_category_id'], ['oltp_main.finance_sub_categories.id'], name='fk_finance_transaction_rules_sub_category'),
        ForeignKeyConstraint(['sub_sub_category_id'], ['oltp_main.finance_sub_sub_categories.id'], name='fk_finance_transaction_rules_sub_sub_category'),
        PrimaryKeyConstraint('id', name='pk_finance_transaction_rules'),
        UniqueConstraint('sheet_id', 'category_id', 'sub_category_id', 'sub_sub_category_id', 'account_name_id', 'actual_budget', name='uq_finance_transaction_rules_combo'),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    sheet_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    category_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sub_category_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sub_sub_category_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    account_name_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    actual_budget: Mapped[ActualBudgetEnum] = mapped_column(Enum(ActualBudgetEnum, values_callable=lambda cls: [member.value for member in cls], name='actual_budget_enum', schema='oltp_main'), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    account_name: Mapped['FinanceAccountNames'] = relationship('FinanceAccountNames', back_populates='finance_transaction_rules')
    category: Mapped['FinanceCategories'] = relationship('FinanceCategories', back_populates='finance_transaction_rules')
    sheet: Mapped['FinanceSheets'] = relationship('FinanceSheets', back_populates='finance_transaction_rules')
    sub_category: Mapped['FinanceSubCategories'] = relationship('FinanceSubCategories', back_populates='finance_transaction_rules')
    sub_sub_category: Mapped['FinanceSubSubCategories'] = relationship('FinanceSubSubCategories', back_populates='finance_transaction_rules')
    finance_transactions: Mapped[list['FinanceTransactions']] = relationship('FinanceTransactions', back_populates='rule')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        ForeignKeyConstraint(['department_id'], ['oltp_main.departments.id'], name='users_id_dept_fkey'),
        ForeignKeyConstraint(['role_id'], ['oltp_main.roles.id'], name='users_id_roles_fkey'),
        PrimaryKeyConstraint('id', name='users_pkey'),
        Index('ix_oltp_main_users_id_dept', 'department_id'),
        Index('ix_oltp_main_users_id_roles', 'role_id'),
        Index('ix_oltp_main_users_nik_active', 'nik', postgresql_where='(deleted_at IS NULL)', unique=True),
        Index('ix_users_public_id', 'public_id', unique=True),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(Integer, Sequence('users_idusers_seq', schema='oltp_main'), primary_key=True)
    nik: Mapped[str] = mapped_column(String(16), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, nullable=False)
    department_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    password: Mapped[Optional[str]] = mapped_column(String(255))
    public_id: Mapped[Optional[str]] = mapped_column(String(22))
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    department: Mapped['Departments'] = relationship('Departments', back_populates='users')
    role: Mapped['Roles'] = relationship('Roles', back_populates='users')
    history: Mapped[list['History']] = relationship('History', back_populates='user')


class History(Base):
    __tablename__ = 'history'
    __table_args__ = (
        ForeignKeyConstraint(['department_id'], ['oltp_main.departments.id'], name='history_upload_id_dept_fkey'),
        ForeignKeyConstraint(['role_id'], ['oltp_main.roles.id'], name='history_upload_id_roles_fkey'),
        ForeignKeyConstraint(['user_id'], ['oltp_main.users.id'], name='history_upload_id_users_fkey'),
        PrimaryKeyConstraint('id', name='history_upload_pkey'),
        UniqueConstraint('public_id', name='history_public_id_unique'),
        Index('ix_history_public_id', 'public_id', unique=True),
        Index('ix_history_upload_public_id', 'public_id'),
        Index('ix_oltp_main_history_upload_id_dept', 'department_id'),
        Index('ix_oltp_main_history_upload_id_roles', 'role_id'),
        Index('ix_oltp_main_history_upload_id_users', 'user_id'),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(Integer, Sequence('history_upload_id_history_upload_seq', schema='oltp_main'), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, nullable=False)
    department_id: Mapped[int] = mapped_column(Integer, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    time_stamp: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    status: Mapped[StatusEnum] = mapped_column(Enum(StatusEnum, values_callable=lambda cls: [member.value for member in cls], name='status_enum', schema='oltp_main'), nullable=False)
    analysis_result: Mapped[Optional[dict]] = mapped_column(JSONB)
    file_name_storage: Mapped[Optional[str]] = mapped_column(String(255))
    note: Mapped[Optional[str]] = mapped_column(Text)
    public_id: Mapped[Optional[str]] = mapped_column(String(22))

    department: Mapped['Departments'] = relationship('Departments', back_populates='history')
    role: Mapped['Roles'] = relationship('Roles', back_populates='history')
    user: Mapped['Users'] = relationship('Users', back_populates='history')
    fact_finance: Mapped[list['FactFinance']] = relationship('FactFinance', back_populates='history')
    finance_transactions: Mapped[list['FinanceTransactions']] = relationship('FinanceTransactions', back_populates='history')
    purchasing_sheet1: Mapped[list['PurchasingSheet1']] = relationship('PurchasingSheet1', back_populates='history')
    purchasing_sheet2: Mapped[list['PurchasingSheet2']] = relationship('PurchasingSheet2', back_populates='history')
    purchasing_sheet3: Mapped[list['PurchasingSheet3']] = relationship('PurchasingSheet3', back_populates='history')


class FactFinance(Base):
    __tablename__ = 'fact_finance'
    __table_args__ = (
        ForeignKeyConstraint(['history_id'], ['oltp_main.history.id'], ondelete='CASCADE', name='fact_finance_id_history_fkey'),
        PrimaryKeyConstraint('id', name='fact_finance_pkey'),
        UniqueConstraint('bulan', 'account_name', 'report_type', 'idx_category', 'category', 'idx_sub_category', 'sub_category', 'sub_sub_category', 'actual_budget', name='uix_finance_data'),
        Index('ix_oltp_main_fact_finance_actual_budget', 'actual_budget'),
        Index('ix_oltp_main_fact_finance_bulan', 'bulan'),
        Index('ix_oltp_main_fact_finance_id_history', 'history_id'),
        Index('ix_oltp_main_fact_finance_report_type', 'report_type'),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(Integer, Sequence('fact_finance_id_fact_seq', schema='oltp_main'), primary_key=True)
    history_id: Mapped[int] = mapped_column(Integer, nullable=False)
    report_type: Mapped[str] = mapped_column(String(10), nullable=False)
    bulan: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    value: Mapped[float] = mapped_column(Double(53), nullable=False)
    idx_category: Mapped[Optional[str]] = mapped_column(String(50))
    category: Mapped[Optional[str]] = mapped_column(String(255))
    idx_sub_category: Mapped[Optional[str]] = mapped_column(String(50))
    sub_category: Mapped[Optional[str]] = mapped_column(String(255))
    sub_sub_category: Mapped[Optional[str]] = mapped_column(String(255))
    account_name: Mapped[Optional[str]] = mapped_column(String(255))
    actual_budget: Mapped[Optional[str]] = mapped_column(String(50))

    history: Mapped['History'] = relationship('History', back_populates='fact_finance')


class FinanceTransactions(Base):
    __tablename__ = 'finance_transactions'
    __table_args__ = (
        ForeignKeyConstraint(['history_id'], ['oltp_main.history.id'], name='fk_oltp_finance_transactions_history'),
        ForeignKeyConstraint(['rule_id'], ['oltp_main.finance_transaction_rules.id'], name='fk_oltp_finance_transactions_rule'),
        PrimaryKeyConstraint('id', name='pk_oltp_finance_transactions'),
        UniqueConstraint('rule_id', 'period_month', name='uq_oltp_finance_transactions_rule_month'),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    history_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rule_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    period_month: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(26, 6), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    history: Mapped['History'] = relationship('History', back_populates='finance_transactions')
    rule: Mapped['FinanceTransactionRules'] = relationship('FinanceTransactionRules', back_populates='finance_transactions')


class PurchasingSheet1(Base):
    __tablename__ = 'purchasing_sheet1'
    __table_args__ = (
        ForeignKeyConstraint(['history_id'], ['oltp_main.history.id'], name='purchasing_sheet1_history_id_fkey'),
        PrimaryKeyConstraint('id', name='purchasing_sheet1_pkey'),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    history_id: Mapped[int] = mapped_column(Integer, nullable=False)
    price_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
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

    history: Mapped['History'] = relationship('History', back_populates='purchasing_sheet1')


class PurchasingSheet2(Base):
    __tablename__ = 'purchasing_sheet2'
    __table_args__ = (
        ForeignKeyConstraint(['history_id'], ['oltp_main.history.id'], name='purchasing_sheet2_history_id_fkey'),
        PrimaryKeyConstraint('id', name='purchasing_sheet2_pkey'),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    history_id: Mapped[int] = mapped_column(Integer, nullable=False)
    variety: Mapped[Optional[str]] = mapped_column(Text)
    list_no: Mapped[Optional[int]] = mapped_column(Integer)
    contract_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    supplier: Mapped[Optional[str]] = mapped_column(Text)
    origin: Mapped[Optional[str]] = mapped_column(Text)
    grade: Mapped[Optional[str]] = mapped_column(Text)
    ton: Mapped[Optional[int]] = mapped_column(Integer)
    price_usd_per_ton_cif: Mapped[Optional[int]] = mapped_column(Integer)
    total_usd: Mapped[Optional[int]] = mapped_column(Integer)
    delivery_detail: Mapped[Optional[str]] = mapped_column(Text)
    delivery: Mapped[Optional[datetime.date]] = mapped_column(Date)
    actual_eta: Mapped[Optional[datetime.date]] = mapped_column(Date)
    delivery_remarks: Mapped[Optional[bool]] = mapped_column(Boolean)
    avg_qty: Mapped[Optional[int]] = mapped_column(Integer)
    avg_value: Mapped[Optional[int]] = mapped_column(Integer)
    avg_price: Mapped[Optional[int]] = mapped_column(Integer)

    history: Mapped['History'] = relationship('History', back_populates='purchasing_sheet2')


class PurchasingSheet3(Base):
    __tablename__ = 'purchasing_sheet3'
    __table_args__ = (
        ForeignKeyConstraint(['history_id'], ['oltp_main.history.id'], name='purchasing_sheet3_history_id_fkey'),
        PrimaryKeyConstraint('id', name='purchasing_sheet3_pkey'),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    history_id: Mapped[int] = mapped_column(Integer, nullable=False)
    variety: Mapped[str] = mapped_column(Text, nullable=False)
    price_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    source_index: Mapped[Optional[int]] = mapped_column(Integer)
    detail: Mapped[Optional[str]] = mapped_column(Text)
    value: Mapped[Optional[int]] = mapped_column(Integer)

    history: Mapped['History'] = relationship('History', back_populates='purchasing_sheet3')
