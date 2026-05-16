from typing import Optional
import datetime
import decimal
import enum

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Enum, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, REAL, Sequence, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


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

    purchasing_sheet2_transactions: Mapped[list['PurchasingSheet2Transactions']] = relationship('PurchasingSheet2Transactions', back_populates='delivery_detail')


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

    purchasing_sheet2_transactions: Mapped[list['PurchasingSheet2Transactions']] = relationship('PurchasingSheet2Transactions', back_populates='grade')


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

    purchasing_sheet2_transactions: Mapped[list['PurchasingSheet2Transactions']] = relationship('PurchasingSheet2Transactions', back_populates='origin')


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

    purchasing_sheet2_transactions: Mapped[list['PurchasingSheet2Transactions']] = relationship('PurchasingSheet2Transactions', back_populates='supplier')


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

    purchasing_sheet2_transactions: Mapped[list['PurchasingSheet2Transactions']] = relationship('PurchasingSheet2Transactions', back_populates='variety')


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
    finance_transactions: Mapped[list['FinanceTransactions']] = relationship('FinanceTransactions', back_populates='history')
    purchasing_sheet1_transactions: Mapped[list['PurchasingSheet1Transactions']] = relationship('PurchasingSheet1Transactions', back_populates='history')
    purchasing_sheet2_transactions: Mapped[list['PurchasingSheet2Transactions']] = relationship('PurchasingSheet2Transactions', back_populates='history')
    purchasing_sheet3_transactions: Mapped[list['PurchasingSheet3Transactions']] = relationship('PurchasingSheet3Transactions', back_populates='history')


class FinanceTransactions(Base):
    __tablename__ = 'finance_transactions'
    __table_args__ = (
        ForeignKeyConstraint(['history_id'], ['oltp_main.history.id'], ondelete='CASCADE', name='fk_stg_finance_transactions_history'),
        ForeignKeyConstraint(['rule_id'], ['oltp_main.finance_transaction_rules.id'], name='fk_stg_finance_transactions_rule'),
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

    history: Mapped['History'] = relationship('History', back_populates='finance_transactions')
    rule: Mapped['FinanceTransactionRules'] = relationship('FinanceTransactionRules', back_populates='finance_transactions')


class PurchasingSheet1Transactions(Base):
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

    history: Mapped['History'] = relationship('History', back_populates='purchasing_sheet1_transactions')


class PurchasingSheet2Transactions(Base):
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
    avg_qty: Mapped[Optional[int]] = mapped_column(BigInteger)
    avg_value: Mapped[Optional[int]] = mapped_column(BigInteger)
    avg_price: Mapped[Optional[int]] = mapped_column(BigInteger)

    delivery_detail: Mapped[Optional['DeliveryDetails']] = relationship('DeliveryDetails', back_populates='purchasing_sheet2_transactions')
    grade: Mapped[Optional['Grades']] = relationship('Grades', back_populates='purchasing_sheet2_transactions')
    history: Mapped['History'] = relationship('History', back_populates='purchasing_sheet2_transactions')
    origin: Mapped[Optional['Origins']] = relationship('Origins', back_populates='purchasing_sheet2_transactions')
    supplier: Mapped[Optional['Suppliers']] = relationship('Suppliers', back_populates='purchasing_sheet2_transactions')
    variety: Mapped['Varieties'] = relationship('Varieties', back_populates='purchasing_sheet2_transactions')


class PurchasingSheet3Transactions(Base):
    __tablename__ = 'purchasing_sheet3_transactions'
    __table_args__ = (
        ForeignKeyConstraint(['history_id'], ['oltp_main.history.id'], ondelete='CASCADE', name='fk_stg_purchasing_sheet3_transactions_history'),
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

    history: Mapped['History'] = relationship('History', back_populates='purchasing_sheet3_transactions')
