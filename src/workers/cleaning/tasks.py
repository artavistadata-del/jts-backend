from src.core.database import celery_app, SessionLocal
from src.infra.upload.schema import ConfirmUploadInput
from src.workers.cleaning.service_factory import get_cleaning_service
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery_app.task(name="cleaning.tasks.analyze_excel_task", bind=True, max_retries=3)
def analyze_excel_task(self, history_id: int, filename: str, id_dept: int):
    db = SessionLocal()
    try:
        service = get_cleaning_service(id_dept, db)
        service.execute_analyze(history_id, filename)
        return f"Analysis complete for ID {history_id}"
    
    except ValueError as ve:
        # ========================================================
        # ERROR VALIDASI / FAIL-FAST: JANGAN LAKUKAN RETRY!
        # ========================================================
        print(f"Validasi Gagal untuk ID {history_id}. Tidak akan di-retry: {ve}")
        raise ve
    
    except Exception as e:
        logger.error(f"Gagal Analisis ID {history_id}: {str(e)}")
        # raise self.retry(exc=e, countdown=60) 
        raise e
    finally:
        db.close()

@celery_app.task(name="cleaning.tasks.commit_upsert_task", bind=True, max_retries=3)
def commit_upsert_task(self, history_id: int, filename: str, id_dept: int, action_value : str):
    db = SessionLocal()
    try:
        service = get_cleaning_service(id_dept, db)
        # service.execute_commit(history_id, filename)
        if action_value == ConfirmUploadInput.CONFIRM.value :
            service.execute_commit(history_id, filename)
            return f"Upsert complete for ID {history_id}"
        elif action_value == ConfirmUploadInput.CANCEL.value :
            service.execute_cancel(history_id, filename)
            return f"Canceled complete for ID {history_id}"
        else :
            return f"Action tidak ada !"

    except ValueError as ve:
        # ========================================================
        # ERROR VALIDASI / FAIL-FAST: JANGAN LAKUKAN RETRY!
        # ========================================================
        print(f"Validasi Gagal untuk ID {history_id}. Tidak akan di-retry: {ve}")
        raise ve
    
    except Exception as e:
        logger.error(f"Gagal Upsert ID {history_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()