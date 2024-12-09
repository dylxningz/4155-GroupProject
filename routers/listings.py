from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from controllers import listings as controller
from schemas import listings as schema
from dependencies.database import get_db
from typing import List, Optional
from sqlalchemy import or_
from models.listings import Listing
from models.tags import Tag  # Use Tag from the correct module

router = APIRouter(
    tags=['Listings'],
    prefix="/listings"
)

@router.post("/", response_model=schema.Listing, status_code=status.HTTP_201_CREATED)
def create_listing(request: schema.ListingCreate, db: Session = Depends(get_db)):
    """
    Create a new listing.
    """
    print(f"Received data: {request.dict()}")  # Debug log
    return controller.create(db=db, request=request)

@router.get("/user/{user_id}", response_model=List[schema.Listing])
def get_listings_by_user(user_id: int, db: Session = Depends(get_db)):
    """
    Fetch listings by a specific user ID.
    """
    listings = db.query(Listing).filter(Listing.user_id == user_id).all()

    if not listings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No items found for this user.")
    
    return listings

@router.get("/", response_model=List[schema.Listing])
def read_all(
    search: Optional[str] = None,
    max_price: Optional[float] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Listing)

    if tag:
       query = query.join(Listing.tags).filter(Tag.tag == tag)  # Correctly join the Tag model

    if search:
        query = query.filter(
            Listing.title.ilike(f"%{search}%") |
            Listing.description.ilike(f"%{search}%")
        )

    if max_price:
        query = query.filter(Listing.price <= max_price)

    return query.all()

@router.get("/{item_id}", response_model=schema.Listing)
def read_one(item_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single listing by its ID.
    """
    return controller.read_one(db, item_id=item_id)

@router.put("/{item_id}", response_model=schema.Listing)
def update(item_id: int, request: schema.ListingUpdate, db: Session = Depends(get_db)):
    """
    Update a listing by its ID.
    """
    return controller.update(db=db, item_id=item_id, request=request)

@router.delete("/{item_id}")
def delete(item_id: int, db: Session = Depends(get_db)):
    """
    Delete a listing by its ID.
    """
    return controller.delete(db=db, item_id=item_id)

@router.get("/tags/{tag_name}", response_model=List[schema.Listing])
def get_listings_by_tag(tag_name: str, db: Session = Depends(get_db)):
    """
    Fetch listings associated with a given tag.
    """
    listings = (
        db.query(Listing)
        .join(Tag)
        .filter(Tag.tag == tag_name)
        .all()
    )

    if not listings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No listings found for this tag.")
    
    return listings