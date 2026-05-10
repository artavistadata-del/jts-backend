from typing import Optional
import datetime
import enum
import shortuuid
from sqlalchemy import Boolean, Date, DateTime, Double, Enum, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, REAL, Sequence, String, Text, UniqueConstraint, text
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


# =========================================
# DEPARTMENTS MODELS
# =========================================
class Departments(Base):
    __tablename__ = 'departments'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='departments_pkey'),
        Index('ix_departments_public_id', 'public_id', unique=True),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(Integer, Sequence('departments_id_dept_seq', schema='oltp_main'), primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(45))
    public_id: Mapped[Optional[str]] = mapped_column(String(22), unique=True, index=True, default=shortuuid.uuid)

    users: Mapped[list['Users']] = relationship('Users', back_populates='department')
    history: Mapped[list['History']] = relationship('History', back_populates='department')

# =========================================
# ROLES MODELS
# =========================================
class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='roles_pkey'),
        Index('ix_roles_public_id', 'public_id', unique=True),
        {'schema': 'oltp_main'}
    )

    id: Mapped[int] = mapped_column(Integer, Sequence('roles_id_roles_seq', schema='oltp_main'), primary_key=True)
    name: Mapped[Optional[RoleEnum]] = mapped_column(Enum(RoleEnum, values_callable=lambda cls: [member.value for member in cls], name='role_enum', schema='oltp_main'))
    public_id: Mapped[Optional[str]] = mapped_column(String(22), unique=True, index=True, default=shortuuid.uuid)

    users: Mapped[list['Users']] = relationship('Users', back_populates='role')
    history: Mapped[list['History']] = relationship('History', back_populates='role')


# =========================================
# USERS MODELS
# =========================================
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
    public_id: Mapped[Optional[str]] = mapped_column(String(22), unique=True, index=True, default=shortuuid.uuid)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    department: Mapped['Departments'] = relationship('Departments', back_populates='users')
    role: Mapped['Roles'] = relationship('Roles', back_populates='users')
    history: Mapped[list['History']] = relationship('History', back_populates='user')


# =========================================
# HISTORY MODELS
# =========================================
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
    public_id: Mapped[Optional[str]] = mapped_column(String(22), unique=True, index=True, default=shortuuid.uuid)

    department: Mapped['Departments'] = relationship('Departments', back_populates='history')
    role: Mapped['Roles'] = relationship('Roles', back_populates='history')
    user: Mapped['Users'] = relationship('Users', back_populates='history')
    fact_finance: Mapped[list['FactFinance']] = relationship('FactFinance', back_populates='history')
    purchasing_sheet1: Mapped[list['PurchasingSheet1']] = relationship('PurchasingSheet1', back_populates='history')
    purchasing_sheet2: Mapped[list['PurchasingSheet2']] = relationship('PurchasingSheet2', back_populates='history')
    purchasing_sheet3: Mapped[list['PurchasingSheet3']] = relationship('PurchasingSheet3', back_populates='history')


# =========================================
# FINANCE MODELS
# =========================================
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


# =========================================
# PURCHASING SHEET 1 MODELS
# =========================================
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

# =========================================
# PURCHASING SHEET 2 MODELS
# =========================================
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

# =========================================
# PURCHASING SHEET 3 MODELS
# =========================================
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
