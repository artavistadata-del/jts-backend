from typing import Optional
import datetime
import enum

from sqlalchemy import Date, Enum, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class RoleEnum(str, enum.Enum):
    STAFF = 'STAFF'
    MANAGER = 'MANAGER'
    DIREKTUR = 'DIREKTUR'
    ADMIN = 'ADMIN'

class StatusEnum(str, enum.Enum):
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'

class Departments(Base):
    __tablename__ = 'departments'
    __table_args__ = {'schema': 'oltp'}

    id_dept: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_dept: Mapped[Optional[str]] = mapped_column(String(45))

    users: Mapped[list['Users']] = relationship('Users', back_populates='departments')
    # Tambahan relasi balik dari history
    history_upload: Mapped[list['HistoryUpload']] = relationship('HistoryUpload', back_populates='departments_history')

class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = {'schema': 'oltp'}

    id_roles: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role: Mapped[Optional[RoleEnum]] = mapped_column(
        Enum(RoleEnum, values_callable=lambda cls: [member.value for member in cls], name='role_enum', schema='oltp')
    )

    users: Mapped[list['Users']] = relationship('Users', back_populates='roles')
    # Tambahan relasi balik dari history
    history_upload: Mapped[list['HistoryUpload']] = relationship('HistoryUpload', back_populates='roles_history')

class Users(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'oltp'}

    idusers: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nik: Mapped[str] = mapped_column(String(16), unique=True, index=True) 
    id_roles: Mapped[int] = mapped_column(Integer, ForeignKey('oltp.roles.id_roles'), index=True)
    id_dept: Mapped[int] = mapped_column(Integer, ForeignKey('oltp.departments.id_dept'), index=True)
    password: Mapped[Optional[str]] = mapped_column(String(255))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default='1')

    departments: Mapped['Departments'] = relationship('Departments', back_populates='users')
    roles: Mapped['Roles'] = relationship('Roles', back_populates='users')
    history_upload: Mapped[list['HistoryUpload']] = relationship('HistoryUpload', back_populates='users')

class HistoryUpload(Base):
    __tablename__ = 'history_upload'
    __table_args__ = {'schema': 'oltp'}

    id_history_upload: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    users_nik: Mapped[str] = mapped_column(String(16), ForeignKey('oltp.users.nik'), index=True)
    
    # --- SNAPSHOT ROLE DAN DEPARTEMEN SAAT UPLOAD ---
    id_roles: Mapped[int] = mapped_column(Integer, ForeignKey('oltp.roles.id_roles'), index=True)
    id_dept: Mapped[int] = mapped_column(Integer, ForeignKey('oltp.departments.id_dept'), index=True)
    
    file_name: Mapped[str] = mapped_column(String(255)) 
    time_stamp: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today)
    
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum, values_callable=lambda cls: [member.value for member in cls], name='status_enum', schema='oltp'),
        default=StatusEnum.PENDING
    )
    is_synced: Mapped[bool] = mapped_column(Boolean, default=False)

    # --- RELATIONSHIPS ---
    users: Mapped['Users'] = relationship('Users', back_populates='history_upload')
    roles_history: Mapped['Roles'] = relationship('Roles', back_populates='history_upload')
    departments_history: Mapped['Departments'] = relationship('Departments', back_populates='history_upload')