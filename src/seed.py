from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.core.config import settings
from src.core.security import get_password_hash

# Pastikan import semua file model agar registry SQLAlchemy lengkap
from src.models.models import *
from src.models.stg_table import *
from src.modules.transaction.finance.models import *
from src.modules.transaction.purchasing.models import *
from src.modules.transaction.sales.models import *

def seed_data():
    db: Session = SessionLocal()
    
    try:
        print("Memulai proses seeding...")

        # 1. Seeding Departments
        departments_data = ['FINANCE','PURCHASING','SALES']
        for dept_name in departments_data:
            existing_dept = db.query(Departments).filter(Departments.name == dept_name).first()
            if not existing_dept:
                new_dept = Departments(name=dept_name)
                db.add(new_dept)
                print(f"Berhasil menambahkan Department: {dept_name}")
        
        # Flush agar ID di-generate sebelum dipakai User
        db.flush() 

        # 2. Seeding Roles
        for role_val in RoleEnum:
            existing_role = db.query(Roles).filter(Roles.name == role_val).first()
            if not existing_role:
                new_role = Roles(name=role_val)
                db.add(new_role)
                print(f"Berhasil menambahkan Role: {role_val.value}")
        
        # Flush agar ID di-generate sebelum dipakai User
        db.flush()

        # 3. Seeding User Admin
        admin_nik = settings.ADMIN_NIK
        existing_user = db.query(Users).filter(Users.nik == admin_nik).first()
        
        if not existing_user:
            # Ambil objek Role ADMIN dan Department FINANCE dari database yang baru di-seed
            admin_role = db.query(Roles).filter(Roles.name == RoleEnum.ADMIN).first()
            finance_dept = db.query(Departments).filter(Departments.name == 'FINANCE').first()

            if admin_role and finance_dept:
                new_admin = Users(
                    nik=admin_nik,
                    name=settings.ADMIN_NAME,
                    password=get_password_hash(settings.ADMIN_PASSWORD),
                    # 👇 PERBAIKAN: Gunakan ID asli dari objek yang baru terbuat di database
                    department_id=finance_dept.id,
                    role_id=admin_role.id
                )
                db.add(new_admin)
                print(f"Berhasil menambahkan User Admin: {settings.ADMIN_NAME}")
            else:
                print("Gagal menambahkan User Admin: Role atau Department tidak ditemukan.")
        else:
            print(f"User dengan NIK {admin_nik} sudah ada, di-skip.")

        # Simpan semua perubahan ke database
        db.commit()
        print("Proses seeding selesai!")

    except Exception as e:
        db.rollback()
        print(f"Terjadi kesalahan saat seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()