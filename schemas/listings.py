from pydantic import BaseModel
from typing import Optional

class ListingBase(BaseModel):
    title: str
    description: str
    price: float

class ListingCreate(ListingBase):
    user_id: int  # This should only be in the ListingCreate schema, as it's required when creating a listing.

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class Listing(ListingBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True