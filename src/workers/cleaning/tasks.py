from sqlalchemy import update

from src.core.database import celery_app, SessionLocal
from src.infra.upload.schema import ConfirmUploadInput
from src.models.models import *
from src.models.stg_table import *
from src.modules.transaction.finance.models import *
from src.modules.transaction.purchasing.models import *
from src.modules.transaction.sales.models import *
from src.workers.cleaning.service_factory import get_cleaning_service
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery_app.task(name="cleaning.tasks.analyze_excel_task", bind=True, max_retries=3)
def analyze_excel_task(self, history_id: int, filename: str, name: str):
    db = SessionLocal()
    try:
        try:
            service = get_cleaning_service(name, db)
        except ValueError as ve:
            error_message = str(ve) 
            
            db.execute(
                update(History)
                .where(History.id == history_id)
                .values(
                    status=StatusEnum.FAILED,
                    analysis_result={"error": error_message}
                )
            )
            db.commit()
            return f"Task dihentikan: {error_message}"
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
        raise e
    finally:
        db.close()

@celery_app.task(name="cleaning.tasks.commit_upsert_task", bind=True, max_retries=3)
def commit_upsert_task(self, history_id: int, filename: str, name: str, action_value : str):
    db = SessionLocal()
    try:
        service = get_cleaning_service(name, db)
        print(action_value)
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