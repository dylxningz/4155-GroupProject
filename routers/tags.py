from fastapi import APIRouter, Depends, FastAPI, status, Response, HTTPException
from sqlalchemy.orm import Session
from controllers import images as controller
from schemas import tags as schema
from dependencies.database import engine, get_db
from fastapi.security import OAuth2PasswordRequestForm
from models import tags as model
from typing import List

router = APIRouter(
    tags=['Tags'],
    prefix="/tags"
)


@router.post("/", response_model=schema.TagResponse, status_code=status.HTTP_201_CREATED)
def create_image(request: schema.TagCreate, db: Session = Depends(get_db)):
   
    return controller.create(db=db, request=request)


@router.get("/tag/{listing_id}", response_model=List[schema.TagResponse])
def get_tags_by_listing(id: int, db: Session = Depends(get_db)):
    listings = db.query(model.Tag).filter(model.Tag.listing_id == id).all()

    if not listings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No items found for this user.")

    return listings


@router.get("/", response_model=list[schema.TagResponse])
def read_all(db: Session = Depends(get_db)):
    return controller.read_all(db)


@router.get("/{tag_id}", response_model=schema.TagResponse)
def read_one(item_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=item_id)


@router.delete("/{item_id}")
def delete(item_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id)