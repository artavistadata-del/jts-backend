from typing import Optional
import datetime
import enum

from sqlalchemy import Date, Enum, Float, ForeignKey, Integer, String, Boolean
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





# # ======================================================================================
# # Insert
# #=========================================================================================

# from typing import Optional
# import datetime
# import enum
# from sqlalchemy import Date, Enum, ForeignKey, Integer, String, Boolean, Float
# from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# # ... (Tabel Roles, Departments, Users, HistoryUpload tetap sama) ...

# class MasterCategory(Base):
#     __tablename__ = 'master_category'
#     __table_args__ = {'schema': 'oltp_tes'}

#     id_category: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     idx_category: Mapped[Optional[str]] = mapped_column(String(50)) # Diset String agar aman untuk Sheet 1 & 2
#     category_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)

#     # Relationships
#     sub_categories: Mapped[list['MasterSubCategory']] = relationship('MasterSubCategory', back_populates='category')
#     data_sheet_1: Mapped[list['DataSheet1']] = relationship('DataSheet1', back_populates='category_rel')
#     data_sheet_2: Mapped[list['DataSheet2']] = relationship('DataSheet2', back_populates='category_rel')


# class MasterSubCategory(Base):
#     __tablename__ = 'master_sub_category'
#     __table_args__ = {'schema': 'oltp_tes'}

#     id_sub_category: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     id_category: Mapped[int] = mapped_column(Integer, ForeignKey('oltp_tes.master_category.id_category', ondelete="CASCADE"), index=True)
#     idx_sub_category: Mapped[Optional[str]] = mapped_column(String(50))
#     sub_category_name: Mapped[str] = mapped_column(String(255), index=True)

#     # Relationships
#     category: Mapped['MasterCategory'] = relationship('MasterCategory', back_populates='sub_categories')
#     data_sheet_1: Mapped[list['DataSheet1']] = relationship('DataSheet1', back_populates='sub_category_rel')
#     data_sheet_2: Mapped[list['DataSheet2']] = relationship('DataSheet2', back_populates='sub_category_rel')

#     sub_sub_categories: Mapped[list['MasterSubSubCategory']] = relationship('MasterSubSubCategory', back_populates='sub_category')

# class MasterSubSubCategory(Base):
#     __tablename__ = 'master_sub_sub_category'
#     __table_args__ = {'schema': 'oltp_tes'}

#     id_sub_sub_category: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     id_sub_category: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('oltp_tes.master_sub_category.id_sub_category', ondelete="CASCADE"), index=True)
#     sub_sub_category_name: Mapped[str] = mapped_column(String(255), index=True)

#     # Relationships
#     sub_category: Mapped['MasterSubCategory'] = relationship('MasterSubCategory', back_populates='sub_sub_categories')
#     data_sheet_1: Mapped[list['DataSheet1']] = relationship('DataSheet1', back_populates='sub_sub_category_rel')


# class MasterAccount(Base):
#     __tablename__ = 'master_account'
#     __table_args__ = {'schema': 'oltp_tes'}

#     id_account: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     account_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)

#     # Relationships
#     data_sheet_1: Mapped[list['DataSheet1']] = relationship('DataSheet1', back_populates='account_rel')
#     data_sheet_2: Mapped[list['DataSheet2']] = relationship('DataSheet2', back_populates='account_rel')


# class DataSheet1(Base):
#     __tablename__ = 'data_sheet_1'
#     __table_args__ = {'schema': 'oltp_tes'}

#     id_data_sheet_1: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     id_history_upload: Mapped[int] = mapped_column(Integer, ForeignKey('oltp_tes.history_upload.id_history_upload', ondelete="CASCADE"), index=True)

#     # Normalisasi: Menggunakan Foreign Key ke Tabel Master
#     id_category: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('oltp_tes.master_category.id_category'), index=True)
#     id_sub_category: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('oltp_tes.master_sub_category.id_sub_category'), index=True)
    
#     # === UBAH BAGIAN INI MENJADI FOREIGN KEY ===
#     id_sub_sub_category: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('oltp_tes.master_sub_sub_category.id_sub_sub_category'), index=True)
    
#     id_account: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('oltp_tes.master_account.id_account'), index=True)
    
#     bulan: Mapped[Optional[datetime.date]] = mapped_column(Date)
#     value: Mapped[Optional[float]] = mapped_column(Float)

#     # Relationships
#     history: Mapped['HistoryUpload'] = relationship('HistoryUpload', back_populates='data_sheet_1')
#     category_rel: Mapped['MasterCategory'] = relationship('MasterCategory', back_populates='data_sheet_1')
#     sub_category_rel: Mapped['MasterSubCategory'] = relationship('MasterSubCategory', back_populates='data_sheet_1')
#     account_rel: Mapped['MasterAccount'] = relationship('MasterAccount', back_populates='data_sheet_1')
#     # === TAMBAHAN RELASI BALIK ===
#     sub_sub_category_rel: Mapped['MasterSubSubCategory'] = relationship('MasterSubSubCategory', back_populates='data_sheet_1')


# class DataSheet2(Base):
#     __tablename__ = 'data_sheet_2'
#     __table_args__ = {'schema': 'oltp_tes'}

#     id_data_sheet_2: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     id_history_upload: Mapped[int] = mapped_column(Integer, ForeignKey('oltp_tes.history_upload.id_history_upload', ondelete="CASCADE"), index=True)

#     # Normalisasi: Menggunakan Foreign Key ke Tabel Master
#     id_category: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('oltp_tes.master_category.id_category'), index=True)
#     id_sub_category: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('oltp_tes.master_sub_category.id_sub_category'), index=True)
#     id_account: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('oltp_tes.master_account.id_account'), index=True)

#     # Kolom yang dibiarkan tetap di tabel transaksi
#     # Kolom transaksi (Sudah disesuaikan menjadi Date dan Float)
#     bulan: Mapped[Optional[datetime.date]] = mapped_column(Date) 
#     value: Mapped[Optional[float]] = mapped_column(Float) # SQLAlchemy Float akan memetakan ke float di database (termasuk Float64)

#     # Relationships
#     history: Mapped['HistoryUpload'] = relationship('HistoryUpload', back_populates='data_sheet_2')
#     category_rel: Mapped['MasterCategory'] = relationship('MasterCategory', back_populates='data_sheet_2')
#     sub_category_rel: Mapped['MasterSubCategory'] = relationship('MasterSubCategory', back_populates='data_sheet_2')
#     account_rel: Mapped['MasterAccount'] = relationship('MasterAccount', back_populates='data_sheet_2')


# class HistoryUpload(Base):
#     __tablename__ = 'history_upload'
#     __table_args__ = {'schema': 'oltp_tes'}

#     id_history_upload: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     users_nik: Mapped[str] = mapped_column(String(16), ForeignKey('oltp_tes.users.nik'), index=True)
    
#     # --- SNAPSHOT ROLE DAN DEPARTEMEN SAAT UPLOAD ---
#     id_roles: Mapped[int] = mapped_column(Integer, ForeignKey('oltp_tes.roles.id_roles'), index=True)
#     id_dept: Mapped[int] = mapped_column(Integer, ForeignKey('oltp_tes.departments.id_dept'), index=True)
    
#     file_name: Mapped[str] = mapped_column(String(255)) 
#     time_stamp: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today)
    
#     status: Mapped[StatusEnum] = mapped_column(
#         Enum(StatusEnum, values_callable=lambda cls: [member.value for member in cls], name='status_enum', schema='oltp_tes'),
#         default=StatusEnum.PENDING
#     )
#     is_synced: Mapped[bool] = mapped_column(Boolean, default=False)

#     # --- RELATIONSHIPS ---
#     users: Mapped['Users'] = relationship('Users', back_populates='history_upload')
#     roles_history: Mapped['Roles'] = relationship('Roles', back_populates='history_upload')
#     departments_history: Mapped['Departments'] = relationship('Departments', back_populates='history_upload')
    
#     # ====== TAMBAHKAN 2 BARIS INI ======
#     data_sheet_1: Mapped[list['DataSheet1']] = relationship('DataSheet1', back_populates='history', cascade="all, delete-orphan")
#     data_sheet_2: Mapped[list['DataSheet2']] = relationship('DataSheet2', back_populates='history', cascade="all, delete-orphan")