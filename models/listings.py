from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from dependencies.database import Base

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"))  # Ensure user cascade if needed
    title = Column(String(150), nullable=False)
    description = Column(String(150), nullable=False)
    price = Column(Float, nullable=False)

    account = relationship("Account", back_populates="listings")
    images = relationship(
        "Image", back_populates="listing", cascade="all, delete-orphan"
    )  
    favorited_by = relationship(
        "Favorite", back_populates="item", cascade="all, delete-orphan"
    )  