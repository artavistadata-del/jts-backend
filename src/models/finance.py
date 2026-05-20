from typing import Optional
import datetime
import decimal
import enum

from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, Enum, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, text
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


class AccountNames(Base):
    __tablename__ = 'account_names'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_finance_account_names'),
        UniqueConstraint('account_name', name='uq_finance_account_names_account_name'),
        {'schema': 'oltp_finance'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    account_name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    transaction_rules: Mapped[list['TransactionRules']] = relationship('TransactionRules', back_populates='account_name')


class Categories(Base):
    __tablename__ = 'categories'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_finance_categories'),
        UniqueConstraint('name', name='uq_finance_categories_name'),
        {'schema': 'oltp_finance'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    transaction_rules: Mapped[list['TransactionRules']] = relationship('TransactionRules', back_populates='category')


class Sheets(Base):
    __tablename__ = 'sheets'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_finance_sheets'),
        UniqueConstraint('name', name='uq_finance_sheets_name'),
        {'schema': 'oltp_finance'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    transaction_rules: Mapped[list['TransactionRules']] = relationship('TransactionRules', back_populates='sheet')


class SubCategories(Base):
    __tablename__ = 'sub_categories'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_finance_sub_categories'),
        UniqueConstraint('name', name='uq_finance_sub_categories_name'),
        {'schema': 'oltp_finance'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    transaction_rules: Mapped[list['TransactionRules']] = relationship('TransactionRules', back_populates='sub_category')


class SubSubCategories(Base):
    __tablename__ = 'sub_sub_categories'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_finance_sub_sub_categories'),
        UniqueConstraint('name', name='uq_finance_sub_sub_categories_name'),
        {'schema': 'oltp_finance'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    is_placeholder: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    transaction_rules: Mapped[list['TransactionRules']] = relationship('TransactionRules', back_populates='sub_sub_category')


t_vw_transaction_rule_lookup = Table(
    'vw_transaction_rule_lookup', Base.metadata,
    Column('rule_id', BigInteger),
    Column('sheet_name', Text),
    Column('category_name', Text),
    Column('sub_category_name', Text),
    Column('sub_sub_category_name', Text),
    Column('account_name', Text),
    Column('actual_budget', Text),
    Column('is_active', Boolean),
    schema='oltp_finance'
)


class Departments(Base):
    __tablename__ = 'departments'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='departments_pkey'),
        Index('ix_departments_public_id', 'public_id', unique=True),
        Index('ix_oltp_main_departments_public_id', 'public_id', unique=True),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(45))
    public_id: Mapped[Optional[str]] = mapped_column(String(22))

    users: Mapped[list['Users']] = relationship('Users', back_populates='department')
    history: Mapped[list['History']] = relationship('History', back_populates='department')


class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='roles_pkey'),
        Index('ix_oltp_main_roles_public_id', 'public_id', unique=True),
        Index('ix_roles_public_id', 'public_id', unique=True),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[Optional[RoleEnum]] = mapped_column(Enum(RoleEnum, values_callable=lambda cls: [member.value for member in cls], name='role_enum', schema='oltp_main'))
    public_id: Mapped[Optional[str]] = mapped_column(String(22))

    users: Mapped[list['Users']] = relationship('Users', back_populates='role')
    history: Mapped[list['History']] = relationship('History', back_populates='role')


class TransactionRules(Base):
    __tablename__ = 'transaction_rules'
    __table_args__ = (
        ForeignKeyConstraint(['account_name_id'], ['oltp_finance.account_names.id'], name='fk_finance_transaction_rules_account_name'),
        ForeignKeyConstraint(['category_id'], ['oltp_finance.categories.id'], name='fk_finance_transaction_rules_category'),
        ForeignKeyConstraint(['sheet_id'], ['oltp_finance.sheets.id'], name='fk_finance_transaction_rules_sheet'),
        ForeignKeyConstraint(['sub_category_id'], ['oltp_finance.sub_categories.id'], name='fk_finance_transaction_rules_sub_category'),
        ForeignKeyConstraint(['sub_sub_category_id'], ['oltp_finance.sub_sub_categories.id'], name='fk_finance_transaction_rules_sub_sub_category'),
        PrimaryKeyConstraint('id', name='pk_finance_transaction_rules'),
        UniqueConstraint('sheet_id', 'category_id', 'sub_category_id', 'sub_sub_category_id', 'account_name_id', 'actual_budget', name='uq_finance_transaction_rules_combo'),
        {'schema': 'oltp_finance'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    sheet_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    category_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sub_category_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sub_sub_category_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    account_name_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    actual_budget: Mapped[ActualBudgetEnum] = mapped_column(Enum(ActualBudgetEnum, values_callable=lambda cls: [member.value for member in cls], name='actual_budget_enum', schema='oltp_finance'), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    account_name: Mapped['AccountNames'] = relationship('AccountNames', back_populates='transaction_rules')
    category: Mapped['Categories'] = relationship('Categories', back_populates='transaction_rules')
    sheet: Mapped['Sheets'] = relationship('Sheets', back_populates='transaction_rules')
    sub_category: Mapped['SubCategories'] = relationship('SubCategories', back_populates='transaction_rules')
    sub_sub_category: Mapped['SubSubCategories'] = relationship('SubSubCategories', back_populates='transaction_rules')
    transactions: Mapped[list['Transactions']] = relationship('Transactions', back_populates='rule')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        ForeignKeyConstraint(['department_id'], ['oltp_main.departments.id'], name='users_id_dept_fkey'),
        ForeignKeyConstraint(['role_id'], ['oltp_main.roles.id'], name='users_id_roles_fkey'),
        PrimaryKeyConstraint('id', name='users_pkey'),
        Index('ix_oltp_main_users_id_dept', 'department_id'),
        Index('ix_oltp_main_users_id_roles', 'role_id'),
        Index('ix_oltp_main_users_nik_active', 'nik', postgresql_where='(deleted_at IS NULL)', unique=True),
        Index('ix_oltp_main_users_public_id', 'public_id', unique=True),
        Index('ix_users_public_id', 'public_id', unique=True),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
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
        Index('ix_oltp_main_history_public_id', 'public_id', unique=True),
        Index('ix_oltp_main_history_upload_id_dept', 'department_id'),
        Index('ix_oltp_main_history_upload_id_roles', 'role_id'),
        Index('ix_oltp_main_history_upload_id_users', 'user_id'),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
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
    transactions: Mapped[list['Transactions']] = relationship('Transactions', back_populates='history')


class Transactions(Base):
    __tablename__ = 'transactions'
    __table_args__ = (
        ForeignKeyConstraint(['history_id'], ['oltp_main.history.id'], name='fk_oltp_finance_transactions_history'),
        ForeignKeyConstraint(['rule_id'], ['oltp_finance.transaction_rules.id'], name='fk_oltp_finance_transactions_rule'),
        PrimaryKeyConstraint('id', name='pk_oltp_finance_transactions'),
        UniqueConstraint('rule_id', 'period_month', name='uq_oltp_finance_transactions_rule_month'),
        {'schema': 'oltp_finance'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    history_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rule_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    period_month: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(26, 6), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    history: Mapped['History'] = relationship('History', back_populates='transactions')
    rule: Mapped['TransactionRules'] = relationship('TransactionRules', back_populates='transactions')
