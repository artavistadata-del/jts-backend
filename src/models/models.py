from typing import Optional
import datetime
import enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Boolean, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class RoleEnum(str, enum.Enum):
    STAFF = 'STAFF'
    MANAGER = 'MANAGER'
    DIREKTUR = 'DIREKTUR'
    ADMIN = 'ADMIN'

class StatusEnum(str, enum.Enum):
    ANALYZING = "ANALYZING"
    AWAITING_PREVIEW = "AWAITING_PREVIEW"
    PROCESSING_INSERT = "PROCESSING_INSERT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class Departments(Base):
    __tablename__ = 'departments'
    __table_args__ = {'schema': 'oltp_main'}

    id_dept: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_dept: Mapped[Optional[str]] = mapped_column(String(45))

    users: Mapped[list['Users']] = relationship('Users', back_populates='departments')
    history_upload: Mapped[list['HistoryUpload']] = relationship('HistoryUpload', back_populates='departments_history')

class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = {'schema': 'oltp_main'}

    id_roles: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role: Mapped[Optional[RoleEnum]] = mapped_column(
        Enum(RoleEnum, values_callable=lambda cls: [member.value for member in cls], name='role_enum', schema='oltp_main')
    )

    users: Mapped[list['Users']] = relationship('Users', back_populates='roles')
    history_upload: Mapped[list['HistoryUpload']] = relationship('HistoryUpload', back_populates='roles_history')

class Users(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'oltp_main'}

    idusers: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nik: Mapped[str] = mapped_column(String(16), unique=True, index=True) 
    id_roles: Mapped[int] = mapped_column(Integer, ForeignKey('oltp_main.roles.id_roles'), index=True)
    id_dept: Mapped[int] = mapped_column(Integer, ForeignKey('oltp_main.departments.id_dept'), index=True)
    password: Mapped[Optional[str]] = mapped_column(String(255))
    nama: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default='1')

    departments: Mapped['Departments'] = relationship('Departments', back_populates='users')
    roles: Mapped['Roles'] = relationship('Roles', back_populates='users')
    history_upload: Mapped[list['HistoryUpload']] = relationship('HistoryUpload', back_populates='users')

class HistoryUpload(Base):
    __tablename__ = 'history_upload'
    __table_args__ = {'schema': 'oltp_main'}

    id_history_upload: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # [PERUBAHAN 1] Mengganti users_nik menjadi id_users (Integer)
    id_users: Mapped[int] = mapped_column(Integer, ForeignKey('oltp_main.users.idusers'), index=True)
    
    id_roles: Mapped[int] = mapped_column(Integer, ForeignKey('oltp_main.roles.id_roles'), index=True)
    id_dept: Mapped[int] = mapped_column(Integer, ForeignKey('oltp_main.departments.id_dept'), index=True)
    
    file_name: Mapped[str] = mapped_column(String(255)) 
    # time_stamp: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today)

    time_stamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), # timezone=True disarankan untuk PostgreSQL
        server_default=func.now()
    )
    
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum, values_callable=lambda cls: [member.value for member in cls], name='status_enum', schema='oltp_main'),
        default=StatusEnum.PENDING
    )

    users: Mapped['Users'] = relationship('Users', back_populates='history_upload')
    roles_history: Mapped['Roles'] = relationship('Roles', back_populates='history_upload')
    departments_history: Mapped['Departments'] = relationship('Departments', back_populates='history_upload')
    finance_data: Mapped[list['FactFinance']] = relationship('FactFinance', back_populates='history', cascade="all, delete-orphan")

    analysis_result = Column(JSONB, nullable=True)
    file_name_storage: Mapped[Optional[str]] = mapped_column(String(255))

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

class FactFinance(Base):
    __tablename__ = 'fact_finance'
    
    # [PERUBAHAN 2] Menambahkan UniqueConstraint ke dalam __table_args__
    __table_args__ = (
        UniqueConstraint(
            'bulan', 'account_name', 'report_type', 'idx_category', 
            'category', 'idx_sub_category', 'sub_category', 'sub_sub_category', 
            name='uix_finance_data'
        ),
        {'schema': 'oltp_main'}
    )

    id_fact: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_history: Mapped[int] = mapped_column(Integer, ForeignKey('oltp_main.history_upload.id_history_upload', ondelete="CASCADE"), index=True)

    report_type: Mapped[str] = mapped_column(String(10), index=True) 

    idx_category: Mapped[Optional[str]] = mapped_column(String(50))
    category: Mapped[Optional[str]] = mapped_column(String(255))
    idx_sub_category: Mapped[Optional[str]] = mapped_column(String(50))
    sub_category: Mapped[Optional[str]] = mapped_column(String(255))
    sub_sub_category: Mapped[Optional[str]] = mapped_column(String(255)) 
    account_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    bulan: Mapped[datetime.date] = mapped_column(Date, index=True)
    value: Mapped[float] = mapped_column(Float)

    history: Mapped['HistoryUpload'] = relationship('HistoryUpload', back_populates='finance_data')