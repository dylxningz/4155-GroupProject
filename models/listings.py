from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from dependencies.database import Base

class Listing(Base):
    __tablename__ = "listings"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("accounts.id"))
    title = Column(String(150), nullable=False)
    description = Column(String(150), unique=False, nullable=False)
    price = Column(Float, nullable=False)

    account = relationship("Account", back_populates="listings")
