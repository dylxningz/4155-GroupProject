from fastapi import APIRouter, Depends, FastAPI, status, Response
from sqlalchemy.orm import Session
from controllers import listings as controller
from schemas import listings as schema
from dependencies.database import engine, get_db

router = APIRouter(
    tags=['Listings'],
    prefix="/listings"
)


@router.post("/", response_model=schema.Listing)
def create(request: schema.ListingCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


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
