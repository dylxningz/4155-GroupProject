from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models.favorite import Favorite
from dependencies.database import get_db
from schemas.favorite import FavoriteCreate, FavoriteResponse

router = APIRouter()

@router.post("/favorite", response_model=FavoriteResponse, tags=["favorites"])
def add_favorite(favorite: FavoriteCreate, db: Session = Depends(get_db)):
    user_id = favorite.user_id
    item_id = favorite.item_id

    existing_favorite = db.query(Favorite).filter_by(user_id=user_id, item_id=item_id).first()
    if existing_favorite:
        raise HTTPException(status_code=409, detail="Item already favorited")

    new_favorite = Favorite(user_id=user_id, item_id=item_id)
    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)
    return new_favorite

@router.get("/favorites", response_model=list[FavoriteResponse], tags=["favorites"])
def list_favorites(user_id: int = Query(...), db: Session = Depends(get_db)):
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")

    favorites = db.query(Favorite).filter(Favorite.user_id == user_id).all()
    return favorites

@router.post("/unfavorite", tags=["favorites"])
def remove_favorite(favorite: FavoriteCreate, db: Session = Depends(get_db)):
    user_id = favorite.user_id
    item_id = favorite.item_id

    existing_favorite = db.query(Favorite).filter_by(user_id=user_id, item_id=item_id).first()
    if not existing_favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    db.delete(existing_favorite)
    db.commit()
    return {"message": "Item unfavorited successfully"}
