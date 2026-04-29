from pydantic import BaseModel


class EditTransactionRequest(BaseModel):
    new_value: float


from pydantic import BaseModel, field_serializer
from datetime import datetime
from zoneinfo import ZoneInfo # Modul bawaan Python 3.9+

class TransactionItemResponse(BaseModel):
    id_history_upload: int
    id_users: int
    id_roles : int
    # id_dept : int
    file_name: str
    notes: str | None = None
    time_stamp: datetime # Ambil tipe data aslinya
    status: str
    nik : str
    nama_user : str


    # Decorator ini akan mencegat data time_stamp sebelum jadi JSON
    @field_serializer('time_stamp')
    def serialize_datetime_to_wib(self, dt: datetime, _info):
        if dt is None:
            return None
        
        # 1. Pastikan datetime dikonversi ke zona waktu Asia/Jakarta
        jakarta_tz = ZoneInfo('Asia/Jakarta')
        wib_dt = dt.astimezone(jakarta_tz)
        
        # 2. Format menjadi string yang rapi (Contoh: "2026-04-29 10:40:56 WIB")
        return wib_dt.strftime("%Y-%m-%d %H:%M:%S WIB")

class TransactionPaginatedResponse(BaseModel):
    items: list[TransactionItemResponse]
    total: int
    page: int
    size: int
    total_pages: int