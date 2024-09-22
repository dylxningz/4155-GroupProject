from pydantic import BaseModel
from typing import Optional


class ListingBase(BaseModel):
    title: str


class ListingCreate(ListingBase):
    user_id: int
    description: str
    price: float


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str]
    price: Optional[float] = None


class Listing(ListingBase):
    id: int
    user_id: int
    title: str
    description: str
    price: float

    class Config:
        from_attributes = True