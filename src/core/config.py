# src/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # =========================================
    # MINIO CONFIG
    # =========================================
    MINIO_URL: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_SECURE: bool = False  # Bisa diatur True saat naik ke Production

    # =========================================
    # POSTGRES CONFIG
    # =========================================
    DATABASE_URL : str

    # =========================================
    # AZURE CONFIG
    # =========================================
    AZURE_TENANT_ID : str
    AZURE_CLIENT_ID : str
    AZURE_CLIENT_SECRET : str

    # =========================================
    # JWT CONFIG
    # =========================================
    SECRET_KEY : str
    ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES : str

    # =========================================
    # REDIS CELERY CONFIG
    # =========================================
    REDIS_URL_CELERY : str

    

    class Config:
        env_file = ".env"


settings = Settings()