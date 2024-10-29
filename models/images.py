from sqlalchemy import Column, Integer, LargeBinary, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from dependencies.database import Base

class Image(Base):
    __tablename__ = "images"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    listing_id = Column(Integer, ForeignKey("listings.id"))
    img_data = Column(LargeBinary)

    listing = relationship("Listing", back_populates="images")