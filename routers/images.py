from fastapi import APIRouter, Depends, FastAPI, status, Response, HTTPException
from sqlalchemy.orm import Session
from controllers import images as controller
from schemas import images as schema
from dependencies.database import engine, get_db
from fastapi.security import OAuth2PasswordRequestForm
from models import images as model
from typing import List

router = APIRouter(
    tags=['Images'],
    prefix="/images"
)


@router.post("/", response_model=schema.Image, status_code=status.HTTP_201_CREATED)
def create_image(request: schema.ImageCreate, db: Session = Depends(get_db)):
    print(f"Received data: {request.dict()}")  # Print incoming data for debugging
    return controller.create(db=db, request=request)


@router.get("/listing/{listing_id}", response_model=List[schema.Image])
def get_images_by_listing(listing_id: int, db: Session = Depends(get_db)):
    # Query to find listings for a specific user
    listings = db.query(model.Image).filter(model.Image.listing_id == listing_id).all()

    if not listings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No items found for this user.")

    return listings


@router.get("/", response_model=list[schema.Image])
def read_all(db: Session = Depends(get_db)):
    return controller.read_all(db)


@router.get("/{item_id}", response_model=schema.Image)
def read_one(item_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=item_id)


@router.put("/{item_id}", response_model=schema.Image)
def update(item_id: int, request: schema.ImageUpdate, db: Session = Depends(get_db)):
    return controller.update(db=db, item_id=item_id, request=request)


@router.delete("/{item_id}")
def delete(item_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id)