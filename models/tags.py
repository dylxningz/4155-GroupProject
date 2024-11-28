from sqlalchemy import Column, Integer, LargeBinary, ForeignKey, String
from sqlalchemy.orm import relationship
from dependencies.database import Base

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    listing_id = Column(Integer, ForeignKey("listings.id", ondelete="CASCADE"))  # Enable cascade delete
    img_data = Column(String(150), nullable=False)

    listing = relationship("Listing", back_populates="tags")