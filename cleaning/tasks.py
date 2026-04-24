from config.config import celery_app
from config.config import SessionLocal
from cleaning.cleaning_service import CleaningService

@celery_app.task(name="cleaning.tasks.process_cleaning_task", bind=True)
def process_cleaning_task(self, history_id: int, filename: str, id_dept: int):
    # Selalu buka dan tutup koneksi DB sendiri di dalam task
    db = SessionLocal()
    try:
        service = CleaningService(db)
        service.run(history_id, filename, id_dept)
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


# cleaning/tasks.py

from config.config import celery_app, SessionLocal
from cleaning.service import BaseCleaningService
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

# ==========================================
# TASK 1: ANALISIS (PREVIEW)
# ==========================================
@celery_app.task(name="cleaning.tasks.analyze_excel_task", bind=True, max_retries=3)
def analyze_excel_task(self, history_id: int, filename: str, id_dept: int):
    """
    Tugas: Mengunduh Excel, membersihkannya, dan membandingkannya 
    dengan database untuk menghitung total Insert vs Replace.
    """
    logger.info(f"Memulai Analisis Preview untuk History ID: {history_id} (Dept: {id_dept})")
    
    # Buka koneksi DB baru khusus untuk worker Celery ini
    db = SessionLocal()
    
    try:
        service = BaseCleaningService(db)
        # Panggil logika inti (Registry & Polars)
        service.execute_analyze(history_id, filename, id_dept)
        
        logger.info(f"Analisis Selesai: History ID {history_id}")
        return f"Analysis complete for ID {history_id}"

    except Exception as e:
        logger.error(f"Gagal Analisis ID {history_id}: {str(e)}")
    
        raise self.retry(exc=e, countdown=60) 
        
    finally:
        # WAJIB: Selalu tutup koneksi agar server 2-Core tidak kehabisan pool koneksi
        db.close()


# ==========================================
# TASK 2: EKSEKUSI (COMMIT UPSERT)
# ==========================================
@celery_app.task(name="cleaning.tasks.commit_upsert_task", bind=True, max_retries=3)
def commit_upsert_task(self, history_id: int, filename: str, id_dept: int):
    """
    Tugas: Mengeksekusi penulisan massal (UPSERT) secara permanen 
    berdasarkan konfirmasi dari Staf (Frontend).
    """
    logger.info(f"Memulai Commit Upsert untuk History ID: {history_id} (Dept: {id_dept})")
    
    db = SessionLocal()
    
    try:
        service = BaseCleaningService(db)
        # Panggil logika inti (SQLAlchemy mass insert)
        service.execute_commit(history_id, filename, id_dept)
        
        logger.info(f"Upsert Selesai: History ID {history_id}")
        return f"Upsert complete for ID {history_id}"

    except Exception as e:
        logger.error(f"Gagal Upsert ID {history_id}: {str(e)}")
        # Coba lagi otomatis jika gagal karena isu sementara
        raise self.retry(exc=e, countdown=60)
        
    finally:
        db.close()