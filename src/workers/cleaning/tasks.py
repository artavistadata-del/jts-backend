from src.core.database import celery_app, SessionLocal
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
    
    except Exception as e:
        logger.error(f"Gagal Analisis ID {history_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60) 
    finally:
        db.close()

@celery_app.task(name="cleaning.tasks.commit_upsert_task", bind=True, max_retries=3)
def commit_upsert_task(self, history_id: int, filename: str, id_dept: int):
    db = SessionLocal()
    try:
        service = get_cleaning_service(id_dept, db)
        service.execute_commit(history_id, filename)
        # if action == 'CONFIRM' :
        #     service.execute_commit(history_id, filename)
        #     return f"Upsert complete for ID {history_id}"
        # elif action == 'CANCEL' :
        #     service.execute_cancel(history_id, filename)
        #     return f"Canceled complete for ID {history_id}"
        # else :
        #     return f"Action tidak ada !"
    except Exception as e:
        logger.error(f"Gagal Upsert ID {history_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()