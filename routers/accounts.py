from fastapi import APIRouter, Depends, FastAPI, status, Response, HTTPException
from sqlalchemy.orm import Session
from controllers import accounts as controller
from schemas import accounts as schema
from dependencies.database import engine, get_db
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    tags=['Accounts'],
    prefix="/accounts"
)

@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Get account by email
    account = controller.get_account_by_email(db, request.username)

    if not account or not controller.verify_password(request.password, account.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Debugging: Print account details
    print(f"Authenticated user: id={account.id}, name={account.name}, email={account.email}")

    # Return id, name, and email
    return {"id": account.id, "name": account.name, "email": account.email}

@router.post("/", response_model=schema.Account)
def create(request: schema.AccountCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.get("/", response_model=list[schema.Account])
def read_all(db: Session = Depends(get_db)):
    return controller.read_all(db)


@router.get("/email/{email}", response_model=schema.Account)
def read_account_by_email(email: str, db: Session = Depends(get_db)):
    return controller.get_account_by_email(db, email)

@router.get("/{item_id}", response_model=schema.Account)
def read_one(item_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=item_id)


@router.put("/{item_id}", response_model=schema.Account)
def update(item_id: int, request: schema.AccountUpdate, db: Session = Depends(get_db)):
    return controller.update(db=db, item_id=item_id, request=request)


@router.delete("/{item_id}")
def delete(item_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id)
