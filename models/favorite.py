from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from dependencies.database import Base

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("listings.id"), nullable=False)

    user = relationship("Account", back_populates="favorites")
    item = relationship("Listing", back_populates="favorited_by")