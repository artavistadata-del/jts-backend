from typing import Optional
import datetime
import decimal
import enum

from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, Enum, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, text
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
    transactions: Mapped[list['FinanceTransactions']] = relationship('FinanceTransactions', back_populates='rule')
    
    staging_transactions: Mapped[list['StagingFinanceTransactions']] = relationship('StagingFinanceTransactions', back_populates='rule')

class FinanceTransactions(Base):
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

    history: Mapped['History'] = relationship('History', back_populates='finance_transactions')
    rule: Mapped['TransactionRules'] = relationship('TransactionRules', back_populates='transactions')
