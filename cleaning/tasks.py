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