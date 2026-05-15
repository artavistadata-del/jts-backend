import io
import polars as pl
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from src.infra.upload.client import minio_client
from src.core.database import engine 
from src.models.models import History, StatusEnum
from src.modules.departments.registry import get_dept_config 
from abc import ABC, abstractmethod

class AbstractCleaningService(ABC):
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
    

    def _pull_data(self, history_id: int, filename: str):
        """
        Menjalankan pull data dari category table master.
        
        Proses meliputi pull semua category data yang nantinya digunakan untuk mapping sebelum insert ke database.
        """
        pass

    def _mapping_data(self, history_id: int, filename: str):
        """
        Menjalankan mapping dari hasil pull data
        
        Proses meliputi mapping dataframe berdasarkan pull data.
        """
        pass

    def _push_data(self, history_id: int, filename: str):
        """
        Menjalankan push data dari hasil mapping
        
        Proses meliputi push data hasil mapping ke staging table.
        """
        pass
    
    @abstractmethod
    def execute_analyze(self, history_id: int, filename: str):
        """
        Menjalankan joining table
        
        Proses meliputi joining staging table dengan oltp.table_transaction.
        Fungsionalitas : 
        1. Cek Row yang akan direplace
        2. Cek Row yang akan diinsert
        """
        pass

    @abstractmethod
    def execute_commit(self, history_id: int, filename: str):
        """
        Menjalankan perintah commit
        
        Proses meliputi insert data dari staging table ke oltp_table_transaction.
        """
        pass

    @abstractmethod
    def execute_cancel(self, history_id: int, filename: str):
        """
        Menjalankan perintah cancel commit
        
        Proses meliputi delete data dari staging table karena tidak di insert   ke oltp_table_transaction.
        """
        pass

    