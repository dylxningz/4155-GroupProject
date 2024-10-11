from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from controllers import accounts as controller
from schemas import accounts as schema
from dependencies.database import get_db
from models.accounts import Account
from passlib.context import CryptContext
from schemas.accounts import AccountUpdate, PasswordChangeRequest
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    tags=['Accounts'],
    prefix="/accounts"
)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str):
    return pwd_context.hash(password)

# Login route
@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    account = controller.get_account_by_email(db, request.username)

    if not account or not verify_password(request.password, account.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"id": account.id, "name": account.name, "email": account.email}

# Create new account
@router.post("/", response_model=schema.Account)
def create(request: schema.AccountCreate, db: Session = Depends(get_db)):
    request.password = hash_password(request.password)  # Hash password before saving
    return controller.create(db=db, request=request)

# Update account profile (name and email)
@router.put("/{user_id}", response_model=schema.Account)
def update_account(user_id: int, request: AccountUpdate, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account.name = request.name if request.name else account.name
    account.email = request.email if request.email else account.email
    db.commit()
    return account

# Change account password
@router.post("/{user_id}/change-password")
def change_password(user_id: int, request: PasswordChangeRequest, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if not verify_password(request.current_password, account.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    account.password = hash_password(request.new_password)
    db.commit()
    return {"message": "Password changed successfully"}

# Retrieve all accounts
@router.get("/", response_model=List[schema.Account])
def read_all(db: Session = Depends(get_db)):
    return controller.read_all(db)

# Retrieve account by email
@router.get("/email/{email}", response_model=schema.Account)
def read_account_by_email(email: str, db: Session = Depends(get_db)):
    return controller.get_account_by_email(db, email)

# Retrieve account by ID
@router.get("/{user_id}", response_model=schema.Account)
def read_one(user_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=user_id)

# Update account (general PUT)
@router.put("/{user_id}", response_model=schema.Account)
def update(user_id: int, request: schema.AccountUpdate, db: Session = Depends(get_db)):
    return controller.update(db=db, item_id=user_id, request=request)

# Delete account
@router.delete("/{user_id}")
def delete(user_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=user_id)