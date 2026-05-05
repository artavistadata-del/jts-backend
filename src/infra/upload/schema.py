from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

from src.models.models import StatusEnum



# ==========================================
# INPUT
# ==========================================
class ConfirmUploadInput(Enum) :
    CONFIRM = 'CONFIRM'
    CANCEL = 'CANCEL'


# BIKIN CLASS INI:
class ConfirmRequest(BaseModel):
    action : ConfirmUploadInput
