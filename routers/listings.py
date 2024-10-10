from fastapi import APIRouter, Depends, FastAPI, status, Response, HTTPException
from sqlalchemy.orm import Session
from controllers import listings as controller
from schemas import listings as schema
from dependencies.database import engine, get_db
from fastapi.security import OAuth2PasswordRequestForm
from models import listings as model
from typing import List

router = APIRouter(
    tags=['Listings'],
    prefix="/listings"
)


@router.post("/", response_model=schema.Listing, status_code=status.HTTP_201_CREATED)
def create_listing(request: schema.ListingCreate, db: Session = Depends(get_db)):
    print(f"Received data: {request.dict()}")  # Print incoming data for debugging
    return controller.create(db=db, request=request)

@router.get("/user/{user_id}", response_model=List[schema.Listing])
def get_listings_by_user(user_id: int, db: Session = Depends(get_db)):
    # Query to find listings for a specific user
    listings = db.query(model.Listing).filter(model.Listing.user_id == user_id).all()

    if not listings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No items found for this user.")
    
    return listings

@router.get("/", response_model=list[schema.Listing])
def read_all(db: Session = Depends(get_db)):
    return controller.read_all(db)


@router.get("/{item_id}", response_model=schema.Listing)
def read_one(item_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=item_id)


@router.put("/{item_id}", response_model=schema.Listing)
def update(item_id: int, request: schema.ListingUpdate, db: Session = Depends(get_db)):
    return controller.update(db=db, item_id=item_id, request=request)


@router.delete("/{item_id}")
def delete(item_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id)
