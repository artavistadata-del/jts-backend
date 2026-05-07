from typing import Optional
import datetime
import enum

from sqlalchemy import Boolean, Date, DateTime, Double, Enum, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, Sequence, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


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


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        ForeignKeyConstraint(['department_id'], ['oltp_main.departments.id'], name='users_id_dept_fkey'),
        ForeignKeyConstraint(['role_id'], ['oltp_main.roles.id'], name='users_id_roles_fkey'),
        PrimaryKeyConstraint('id', name='users_pkey'),
        Index('ix_oltp_main_users_id_dept', 'department_id'),
        Index('ix_oltp_main_users_id_roles', 'role_id'),
        Index('ix_oltp_main_users_nik', 'nik', unique=True),
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
    notes: Mapped[Optional[str]] = mapped_column(Text)
    public_id: Mapped[Optional[str]] = mapped_column(String(22))

    department: Mapped['Departments'] = relationship('Departments', back_populates='history')
    role: Mapped['Roles'] = relationship('Roles', back_populates='history')
    user: Mapped['Users'] = relationship('Users', back_populates='history')
    fact_finance: Mapped[list['FactFinance']] = relationship('FactFinance', back_populates='history')


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
