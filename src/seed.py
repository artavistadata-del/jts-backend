from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.core.config import settings
# Ganti 'nama_file_model_anda' dengan nama file tempat class-class ini berada
from src.core.security import get_password_hash
from src.models.models import Departments, Roles, RoleEnum, Users 

def seed_data():
    db: Session = SessionLocal()
    
    try:
        print("Memulai proses seeding...")

        # 1. Seeding Departments
        departments_data = ['FINANCE', 'PURCHASING']
        for dept_name in departments_data:
            existing_dept = db.query(Departments).filter(Departments.name == dept_name).first()
            if not existing_dept:
                new_dept = Departments(name=dept_name)
                db.add(new_dept)
                print(f"Berhasil menambahkan Department: {dept_name}")
        
        # Flush agar ID department-nya di-generate sebelum dipakai oleh User
        db.flush() 

        # 2. Seeding Roles
        for role_val in RoleEnum:
            existing_role = db.query(Roles).filter(Roles.name == role_val).first()
            if not existing_role:
                new_role = Roles(name=role_val)
                db.add(new_role)
                print(f"Berhasil menambahkan Role: {role_val.value}")
        
        # Flush agar ID role-nya di-generate sebelum dipakai oleh User
        db.flush()

        # 3. Seeding User Admin
        admin_nik = settings.ADMIN_NIK
        existing_user = db.query(Users).filter(Users.nik == admin_nik).first()
        
        if not existing_user:
            # Ambil objek Role ADMIN dan Department FINANCE dari database yang baru saja di-seed
            admin_role = db.query(Roles).filter(Roles.name == RoleEnum.ADMIN).first()
            finance_dept = db.query(Departments).filter(Departments.name == 'FINANCE').first()

            if admin_role and finance_dept:
                new_admin = Users(
                    nik=admin_nik,
                    name=settings.ADMIN_NAME,
                    password=get_password_hash(settings.ADMIN_PASSWORD),
                    department_id=settings.ADMIN_DEPARTMENT_ID,
                    role_id=settings.ADMIN_ROLE_ID
                )
                db.add(new_admin)
                print(f"Berhasil menambahkan User Admin: ALBERTO")
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