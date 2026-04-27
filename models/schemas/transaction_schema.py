from pydantic import BaseModel


class EditTransactionRequest(BaseModel):
    new_value: float