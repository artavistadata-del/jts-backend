from pydantic import BaseModel, Field

class User(BaseModel) :
    nik : str = Field(..., min_length=16, max_length=16)
    password : str = Field(..., min_length=8,max_length=72)