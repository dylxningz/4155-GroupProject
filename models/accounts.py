from sqlalchemy import Column, Date, Integer, String,DateTime, Boolean
from sqlalchemy.orm import mapped_column, relationship
from dependencies.database import Base
from sqlalchemy.sql import func

class Account(Base):
    __tablename__ = "accounts"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    is_verified = Column(Boolean, default=False)  # Track verification status
    verification_code = Column(String(100), nullable=True)  # Temporary code (hashed)
    code_expiration = Column(DateTime, nullable=True)


    listings = relationship("Listing", back_populates="account", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
