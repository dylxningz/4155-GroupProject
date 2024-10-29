from pydantic import BaseModel
from typing import Optional

class ImageBase(BaseModel):
    img_data: bytes

class ImageCreate(ImageBase):
    listing_id: int

class ImageUpdate(BaseModel):
    img_data: Optional[bytes] = None

class Image(ImageBase):
    id: int
    listing_id: int

    class Config:
        from_attributes = True