from pydantic import BaseModel

class TagCreate(BaseModel):
    tag: str
    listing_id: int

class TagResponse(BaseModel):
    id: int
    tag: str
    listing_id: int

    class Config:
        orm_mode = True