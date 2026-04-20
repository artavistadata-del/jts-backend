from typing import Optional
import datetime
import enum

from sqlalchemy import Date, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class RoleEnum(str, enum.Enum):
    STAFF = 'STAFF'
    MANAGER = 'MANAGER'


class Departments(Base):
    __tablename__ = 'departments'
    __table_args__ = {'schema': 'mydb'}

    # Primary Key Tunggal
    id_dept: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_dept: Mapped[Optional[str]] = mapped_column(String(45))

    # Relationships
    users: Mapped[list['Users']] = relationship('Users', back_populates='departments')
    history_upload: Mapped[list['HistoryUpload']] = relationship('HistoryUpload', back_populates='departments_dept')


class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = {'schema': 'mydb'}

    # Primary Key Tunggal
    id_roles: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role: Mapped[Optional[RoleEnum]] = mapped_column(
        Enum(RoleEnum, values_callable=lambda cls: [member.value for member in cls], name='role_enum', schema='mydb')
    )

    # Relationships
    users: Mapped[list['Users']] = relationship('Users', back_populates='roles')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        UniqueConstraint('nik', name='users_nik_key'), # NIK harus unik
        {'schema': 'mydb'}
    )

    # 1. SATU-SATUNYA Primary Key di tabel ini, bisa autoincrement
    idusers: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 2. Kolom biasa (Bukan Primary Key)
    nik: Mapped[str] = mapped_column(String(16), index=True) 
    
    # 3. Foreign Keys (Langsung didefinisikan di kolom agar rapi)
    id_roles: Mapped[int] = mapped_column(Integer, ForeignKey('mydb.roles.id_roles'), index=True)
    id_dept: Mapped[int] = mapped_column(Integer, ForeignKey('mydb.departments.id_dept'), index=True)
    
    # 4. Password sudah menggunakan 255 karakter
    password: Mapped[Optional[str]] = mapped_column(String(255))

    # Relationships
    departments: Mapped['Departments'] = relationship('Departments', back_populates='users')
    roles: Mapped['Roles'] = relationship('Roles', back_populates='users')
    history_upload: Mapped[list['HistoryUpload']] = relationship('HistoryUpload', back_populates='users')


class HistoryUpload(Base):
    __tablename__ = 'history_upload'
    __table_args__ = {'schema': 'mydb'}

    # 1. SATU-SATUNYA Primary Key
    id_history_upload: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 2. Foreign Keys 
    users_nik: Mapped[str] = mapped_column(String(16), ForeignKey('mydb.users.nik'), index=True)
    departments_id_dept: Mapped[int] = mapped_column(Integer, ForeignKey('mydb.departments.id_dept'), index=True)
    
    # 3. Kolom data
    file_name: Mapped[Optional[str]] = mapped_column(String(45))
    time_stamp: Mapped[Optional[datetime.date]] = mapped_column(Date)

    # Relationships
    departments_dept: Mapped['Departments'] = relationship('Departments', back_populates='history_upload')
    users: Mapped['Users'] = relationship('Users', back_populates='history_upload')