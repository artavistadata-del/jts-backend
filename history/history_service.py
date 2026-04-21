from models.models.models import HistoryUpload as HistoryUploadModels
from models.schemas.history_schema import HistoryUpload as HistoryUploadSchema
from history.history_repository import HistoryRepository 


class HistoryService :
    def __init__(self, history_repo : HistoryRepository):
        self.history_repo = history_repo

    def add_history(self, history_schema : HistoryUploadSchema):
        history_models = HistoryUploadModels(
            users_nik = history_schema.users_nik,
            id_roles = history_schema.id_role,
            id_dept = history_schema.id_dept,
            file_name = history_schema.file_name,
            time_stamp = history_schema.time_stamp
    
        )
        # history_models = HistoryUploadModels(
        #     users_nik = history_schema.users_nik,
        #     departments_id_dept = history_schema.id_dept,    
        #     file_name = history_schema.file_name,
        #     time_stamp = history_schema.time_stamp
        # )
        self.history_repo.insert_history(history_models)

        return 'History Berhasil Ditambahkan'