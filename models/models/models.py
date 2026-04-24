from typing import Optional
import datetime
import enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Date, Enum, Float, ForeignKey, Integer, String, Boolean
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

class Departments(Base):
    __tablename__ = 'departments'
    __table_args__ = {'schema': 'oltp_tes'}

    id_dept: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_dept: Mapped[Optional[str]] = mapped_column(String(45))

    users: Mapped[list['Users']] = relationship('Users', back_populates='departments')
    history_upload: Mapped[list['HistoryUpload']] = relationship('HistoryUpload', back_populates='departments_history')

class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = {'schema': 'oltp_tes'}

    id_roles: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role: Mapped[Optional[RoleEnum]] = mapped_column(
        Enum(RoleEnum, values_callable=lambda cls: [member.value for member in cls], name='role_enum', schema='oltp_tes')
    )

    users: Mapped[list['Users']] = relationship('Users', back_populates='roles')
    history_upload: Mapped[list['HistoryUpload']] = relationship('HistoryUpload', back_populates='roles_history')

class Users(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'oltp_tes'}

    idusers: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nik: Mapped[str] = mapped_column(String(16), unique=True, index=True) 
    id_roles: Mapped[int] = mapped_column(Integer, ForeignKey('oltp_tes.roles.id_roles'), index=True)
    id_dept: Mapped[int] = mapped_column(Integer, ForeignKey('oltp_tes.departments.id_dept'), index=True)
    password: Mapped[Optional[str]] = mapped_column(String(255))

    nama: Mapped[str] = mapped_column(String(255))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default='1')

    departments: Mapped['Departments'] = relationship('Departments', back_populates='users')
    roles: Mapped['Roles'] = relationship('Roles', back_populates='users')
    history_upload: Mapped[list['HistoryUpload']] = relationship('HistoryUpload', back_populates='users')

class HistoryUpload(Base):
    __tablename__ = 'history_upload'
    __table_args__ = {'schema': 'oltp_tes'}

    id_history_upload: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    users_nik: Mapped[str] = mapped_column(String(16), ForeignKey('oltp_tes.users.nik'), index=True)
    
    id_roles: Mapped[int] = mapped_column(Integer, ForeignKey('oltp_tes.roles.id_roles'), index=True)
    id_dept: Mapped[int] = mapped_column(Integer, ForeignKey('oltp_tes.departments.id_dept'), index=True)
    
    file_name: Mapped[str] = mapped_column(String(255)) 
    time_stamp: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today)
    
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum, values_callable=lambda cls: [member.value for member in cls], name='status_enum', schema='oltp_tes'),
        default=StatusEnum.PENDING
    )
    is_synced: Mapped[bool] = mapped_column(Boolean, default=False)

    users: Mapped['Users'] = relationship('Users', back_populates='history_upload')
    roles_history: Mapped['Roles'] = relationship('Roles', back_populates='history_upload')
    departments_history: Mapped['Departments'] = relationship('Departments', back_populates='history_upload')
    finance_data: Mapped[list['FactFinance']] = relationship('FactFinance', back_populates='history', cascade="all, delete-orphan")

    analysis_result = Column(JSONB, nullable=True)
class FactFinance(Base):
    __tablename__ = 'fact_finance'
    __table_args__ = {'schema': 'oltp_tes'}

    id_fact: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_history: Mapped[int] = mapped_column(Integer, ForeignKey('oltp_tes.history_upload.id_history_upload', ondelete="CASCADE"), index=True)

    # Penanda dari sheet mana data ini berasal ('BS' atau 'IS')
    report_type: Mapped[str] = mapped_column(String(10), index=True) 

    # Kolom dari Excel
    idx_category: Mapped[Optional[str]] = mapped_column(String(50))
    category: Mapped[Optional[str]] = mapped_column(String(255))
    idx_sub_category: Mapped[Optional[str]] = mapped_column(String(50))
    sub_category: Mapped[Optional[str]] = mapped_column(String(255))
    sub_sub_category: Mapped[Optional[str]] = mapped_column(String(255)) # Data IS akan masuk sebagai NULL di sini
    account_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    bulan: Mapped[datetime.date] = mapped_column(Date, index=True)
    value: Mapped[float] = mapped_column(Float)

    history: Mapped['HistoryUpload'] = relationship('HistoryUpload', back_populates='finance_data')