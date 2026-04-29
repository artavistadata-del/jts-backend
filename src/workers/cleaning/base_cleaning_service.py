import io
import polars as pl
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from src.config.minio_conf import minio_client
from src.config.config import engine 
from src.models.models.models import HistoryUpload, StatusEnum
from src.config.dept_registry import get_dept_config 

class BaseCleaningService:
    def __init__(self, db_session):
        self.db = db_session
        self.minio = minio_client

    def _download_and_clean(self, history_id: int, filename: str, id_dept: int, cleanser_func) -> pl.DataFrame:
        """Fungsi generik untuk unduh dan bersihkan Excel."""
        # raw_bucket = f"raw-dept-{id_dept}"
        raw_bucket = get_dept_config(id_dept)
        raw_bucket = raw_bucket['name']
        
        response = self.minio.get_object(raw_bucket, filename)
        raw_bytes = io.BytesIO(response.read())
        response.close()
        response.release_conn()

        return cleanser_func(raw_bytes, history_id)