from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from controllers import accounts as controller
from schemas import accounts as schema
from dependencies.database import get_db
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    tags=['Accounts'],
    prefix="/accounts"
)

# Login route
@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print("FastAPI login endpoint hit")
    account = controller.get_account_by_email(db, request.username)
    print(f"Account fetched: {account}")

    if not account or not controller.verify_password(request.password, account.password):
        print("Invalid credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not account.is_verified:
        print("Account not verified")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )

    print("Login successful")
    return {"id": account.id, "name": account.name, "email": account.email}
# Create new account (signup)
@router.post("/", response_model=schema.Account)
def create(request: schema.AccountCreate, db: Session = Depends(get_db)):
    return controller.create(db, request)

# Verify email
@router.post("/verify")
def verify_email(email: str, code: str, db: Session = Depends(get_db)):
    return controller.verify_email(db=db, email=email, code=code)

# Resend verification email
@router.post("/resend-verification")
def resend_verification(email: str, db: Session = Depends(get_db)):
    return controller.resend_verification(db=db, email=email)

# Update account profile (name and email)
@router.put("/{user_id}", response_model=schema.Account)
def update_account(user_id: int, request: schema.AccountUpdate, db: Session = Depends(get_db)):
    return controller.update(db=db, item_id=user_id, request=request)

# Change account password
@router.post("/{user_id}/change-password")
def change_password(user_id: int, request: schema.PasswordChangeRequest, db: Session = Depends(get_db)):
    account = controller.read_one(db, user_id)
    if not controller.verify_password(request.current_password, account.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    account.password = controller.hash_password(request.new_password)
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

# Delete account
@router.delete("/{user_id}")
def delete(user_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=user_id)
