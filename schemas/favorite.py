from pydantic import BaseModel

class FavoriteCreate(BaseModel):
    user_id: int
    item_id: int

class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    item_id: int

    class Config:
        orm_mode = True