from typing import Optional
import datetime
import enum

from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, Enum, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from src.core.database import Base


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


class SalesSources(Base):
    __tablename__ = 'sources'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='sources_pkey'),
        UniqueConstraint('name', name='sources_name_key'),
        {'schema': 'oltp_sales'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    transactions: Mapped[list['SalesTransactions']] = relationship('SalesTransactions', back_populates='source')
    staging_transactions: Mapped[list['StagingSalesTransactions']] = relationship('StagingSalesTransactions', back_populates='source')


class SalesProducts(Base):
    __tablename__ = 'products'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='products_pkey'),
        UniqueConstraint('name', name='products_name_key'),
        {'schema': 'oltp_sales'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    transactions: Mapped[list['SalesTransactions']] = relationship('SalesTransactions', back_populates='product')
    staging_transactions: Mapped[list['StagingSalesTransactions']] = relationship('StagingSalesTransactions', back_populates='product')

class SalesGrades(Base):
    __tablename__ = 'grades'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='grades_pkey'),
        UniqueConstraint('name', name='grades_name_key'),
        {'schema': 'oltp_sales'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    transactions: Mapped[list['SalesTransactions']] = relationship('SalesTransactions', back_populates='grade')
    staging_transactions: Mapped[list['StagingSalesTransactions']] = relationship('StagingSalesTransactions', back_populates='grade')


t_vw_all_masters = Table(
    'vw_all_masters', Base.metadata,
    Column('master_type', Text),
    Column('master_id', Integer),
    Column('master_name', String),
    schema='oltp_sales'
)


class Weeks(Base):
    __tablename__ = 'weeks'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_sales_week'),
        {'schema': 'oltp_sales'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)

    transactions: Mapped[list['SalesTransactions']] = relationship('SalesTransactions', back_populates='week')
    staging_transactions: Mapped[list['StagingSalesTransactions']] = relationship('StagingSalesTransactions', back_populates='week')


class SalesTransactions(Base):
    __tablename__ = 'transactions'
    __table_args__ = (
        ForeignKeyConstraint(['source_id'], ['oltp_sales.sources.id'], ondelete='RESTRICT', name='fk_sales_source'),
        ForeignKeyConstraint(['product_id'], ['oltp_sales.products.id'], ondelete='RESTRICT', name='fk_sales_product'),
        ForeignKeyConstraint(['grade_id'], ['oltp_sales.grades.id'], ondelete='RESTRICT', name='fk_sales_grade'),
        ForeignKeyConstraint(['history_id'], ['oltp_main.history.id'], ondelete='RESTRICT', name='fk_sales_history'),
        ForeignKeyConstraint(['week_id'], ['oltp_sales.weeks.id'], ondelete='RESTRICT', name='fk_sales_week'),
        PrimaryKeyConstraint('id', name='transactions_pkey'),
        # Kombinasi unik disesuaikan untuk memasukkan source_id dan product_id
        UniqueConstraint('date', 'source_id', 'product_id', 'grade_id', 'week_id', name='uq_transaction_combination'),
        {'schema': 'oltp_sales'}
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

    # Definisi relationship
    source: Mapped['SalesSources'] = relationship('SalesSources', back_populates='transactions')
    product: Mapped['SalesProducts'] = relationship('SalesProducts', back_populates='transactions')
    grade: Mapped['SalesGrades'] = relationship('SalesGrades', back_populates='transactions')
    history: Mapped['History'] = relationship('History', back_populates='sales_transactions')
    week: Mapped['Weeks'] = relationship('Weeks', back_populates='transactions')
