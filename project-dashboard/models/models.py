from sqlalchemy import Column, Integer, String
from config.config import Base


class User(Base) :
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    nik = Column(String(16), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)