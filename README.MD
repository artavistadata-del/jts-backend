celery :

1. cd ~/jts-project/project-dashboard
2. celery -A src.workers.celery_app worker --loglevel=info

fastAPI :

1. cd ~/jts-project/project-dashboard
2. uvicorn src.main:app --host 0.0.0.0 --port 8881 --reload

📁 backend/
├── 📄 main.py # Entry point aplikasi (FastAPI instance)
├── 📁 api/ # Kumpulan rute utama
│ └── 📄 v1_router.py # Menggabungkan router users, history, dll ke /v1
│
├── 📁 core/ # Jantung konfigurasi aplikasi
│ ├── 📄 config.py # Baca .env dan variabel global
│ ├── 📄 security.py # JWT, Hashing, get_current_user
│ ├── 📄 dependencies.py # Dependensi global seperti get_db
│ └── 📄 exceptions.py # Custom error handler (Opsional)
│
├── 📁 models/ # MURNI HANYA UNTUK SQLALCHEMY
│ ├── 📄 base.py # Deklarasi Base = declarative_base()
│ ├── 📄 users.py # Model tabel users
│ ├── 📄 history.py # Model tabel history
│ └── 📄 transactions.py # Model tabel transaksi
│
├── 📁 modules/ # (Atau 'domain/') BERISI LOGIKA BISNIS
│ ├── 📁 users/
│ │ ├── 📄 router.py # (Ganti nama user_route.py jadi router.py)
│ │ ├── 📄 service.py  
│ │ ├── 📄 repository.py
│ │ └── 📄 schemas.py # Pydantic schema khusus untuk User
│ │
│ ├── 📁 history/
│ │ ├── 📄 router.py
│ │ ├── 📄 service.py
│ │ ├── 📄 repository.py
│ │ └── 📄 schemas.py # Pydantic schema khusus untuk History
│ │
│ ├── 📁 departments/ # (Sama seperti di atas: router, service, repo, schema)
│ └── 📁 roles/ # (Sama seperti di atas)
│
├── 📁 infra/ # INTEGRASI PIHAK KETIGA
│ ├── 📁 minio/ # Pindahan dari folder 'upload' dan 'config/minio_conf'
│ │ ├── 📄 client.py # Setup koneksi Minio
│ │ └── 📄 service.py # Logika upload ke Minio
│ │
│ └── 📁 powerbi/ # Pindahan dari 'powerbi' dan 'config/powerbi_conf'
│ └── 📄 client.py
│
└── 📁 workers/ # BACKGROUND TASKS & DATA PROCESSING
├── 📄 celery_app.py # Inisialisasi Celery
├── 📄 tasks.py # Kumpulan @celery.task
└── 📁 data_cleaning/ # Gabungan dari folder 'cleaners' dan 'cleaning'
├── 📄 base.py # base_cleaning_service.py
└── 📄 finance.py # finance_cleanser.py
