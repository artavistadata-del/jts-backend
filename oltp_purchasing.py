from typing import Optional
import datetime
import enum

from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, Enum, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, REAL, Sequence, String, Table, Text, UniqueConstraint, text
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

    sheet2_transactions: Mapped[list['Sheet2Transactions']] = relationship('Sheet2Transactions', back_populates='delivery_detail')


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

    sheet2_transactions: Mapped[list['Sheet2Transactions']] = relationship('Sheet2Transactions', back_populates='grade')


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

    sheet2_transactions: Mapped[list['Sheet2Transactions']] = relationship('Sheet2Transactions', back_populates='origin')


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

    sheet2_transactions: Mapped[list['Sheet2Transactions']] = relationship('Sheet2Transactions', back_populates='supplier')


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
    sheet2_transactions: Mapped[list['Sheet2Transactions']] = relationship('Sheet2Transactions', back_populates='variety')


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
    sheet3_transactions: Mapped[list['Sheet3Transactions']] = relationship('Sheet3Transactions', back_populates='rule')


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
    sheet1_transactions: Mapped[list['Sheet1Transactions']] = relationship('Sheet1Transactions', back_populates='history')
    sheet2_transactions: Mapped[list['Sheet2Transactions']] = relationship('Sheet2Transactions', back_populates='history')
    sheet3_transactions: Mapped[list['Sheet3Transactions']] = relationship('Sheet3Transactions', back_populates='history')


class Sheet1Transactions(Base):
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

    history: Mapped['History'] = relationship('History', back_populates='sheet1_transactions')


class Sheet2Transactions(Base):
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
    avg_qty: Mapped[Optional[int]] = mapped_column(BigInteger)
    avg_value: Mapped[Optional[int]] = mapped_column(BigInteger)
    avg_price: Mapped[Optional[int]] = mapped_column(BigInteger)

    delivery_detail: Mapped[Optional['DeliveryDetails']] = relationship('DeliveryDetails', back_populates='sheet2_transactions')
    grade: Mapped[Optional['Grades']] = relationship('Grades', back_populates='sheet2_transactions')
    history: Mapped['History'] = relationship('History', back_populates='sheet2_transactions')
    origin: Mapped[Optional['Origins']] = relationship('Origins', back_populates='sheet2_transactions')
    supplier: Mapped[Optional['Suppliers']] = relationship('Suppliers', back_populates='sheet2_transactions')
    variety: Mapped['Varieties'] = relationship('Varieties', back_populates='sheet2_transactions')


class Sheet3Transactions(Base):
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
    value: Mapped[Optional[int]] = mapped_column(BigInteger)

    history: Mapped['History'] = relationship('History', back_populates='sheet3_transactions')
    rule: Mapped['Sheet3TransactionRules'] = relationship('Sheet3TransactionRules', back_populates='sheet3_transactions')
