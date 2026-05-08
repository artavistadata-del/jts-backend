from datetime import date
from enum import Enum

from pydantic import BaseModel

from src.models.models import Base


class DepartmentEnum(str, Enum) :
    FINANCE = 'FINANCE'
    ACCOUNTING = 'ACCOUNTING'

class DepartmentsInsertSchema(BaseModel):
    name : str


class DepartmentsUpdateSchema(BaseModel) :
    name : str

