from datetime import date
from enum import Enum

from pydantic import BaseModel

from src.models.models import Base


class DepartmentEnum(str, Enum) :
    FINANCE = 'FINANCE'
    ACCOUNTING = 'ACCOUNTING'

class DepartmentsInsertSchema(BaseModel):
    dept_name : str

