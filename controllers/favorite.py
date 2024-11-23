from sqlalchemy.orm import Session
from models.favorite import Favorite
from schemas.favorite import FavoriteCreate

def create_favorite(db: Session, user_id: int, item_id: int):
    favorite = Favorite(user_id=user_id, item_id=item_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite

def get_user_favorites(db: Session, user_id: int):
    return db.query(Favorite).filter(Favorite.user_id == user_id).all()
