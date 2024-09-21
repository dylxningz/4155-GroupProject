from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.orm import mapped_column
from dependencies.database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
