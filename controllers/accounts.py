from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response, Depends, exceptions
from models import accounts as model
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext
import hashlib
from utilities.email_utils import send_verification_email

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create(db: Session, request):
    # Hash the password before saving it
    hashed_password = hash_password(request.password)

    # Generate verification code and expiration time
    verification_code = hashlib.sha256(str(datetime.utcnow()).encode()).hexdigest()[:6]
    expiration_time = datetime.utcnow() + timedelta(minutes=30)

    new_item = model.Account(
        name=request.name,
        email=request.email,
        password=hashed_password,
        verification_code=hashlib.sha256(verification_code.encode()).hexdigest(),
        code_expiration=expiration_time,
        is_verified=False,
    )

    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        # Send the verification email
        send_verification_email(request.email, verification_code)
    except exceptions.ResponseValidationError as e:
        new_item.id = 0
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    return new_item


def verify_email(db: Session, email: str, code: str):
    # Fetch the account by email
    account = db.query(model.Account).filter(model.Account.email == email).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found.")

    # Check if the code has expired
    if datetime.utcnow() > account.code_expiration:
        raise HTTPException(status_code=400, detail="Verification code has expired.")

    # Validate the verification code
    hashed_code = hashlib.sha256(code.encode()).hexdigest()
    if account.verification_code != hashed_code:
        raise HTTPException(status_code=400, detail="Invalid verification code.")

    # Mark the account as verified
    account.is_verified = True
    account.verification_code = None
    account.code_expiration = None
    db.commit()

    return {"message": "Email verified successfully."}


def resend_verification(db: Session, email: str):
    # Fetch the account by email
    account = db.query(model.Account).filter(model.Account.email == email).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found.")

    if account.is_verified:
        return {"message": "Account is already verified."}

    # Generate a new verification code
    verification_code = hashlib.sha256(str(datetime.utcnow()).encode()).hexdigest()[:6]
    expiration_time = datetime.utcnow() + timedelta(minutes=30)

    account.verification_code = hashlib.sha256(verification_code.encode()).hexdigest()
    account.code_expiration = expiration_time
    db.commit()

    # Send the verification email
    try:
        send_verification_email(email, verification_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    return {"message": "Verification code resent successfully."}

def read_all(db: Session):
    try:
        result = db.query(model.Account).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result


def read_one(db: Session, item_id):
    try:
        item = db.query(model.Account).filter(model.Account.id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def get_account_by_email(db: Session, item_email: str):
    try:
        item = db.query(model.Account).filter(model.Account.email == item_email).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item



def update(db: Session, item_id, request):
    try:
        item = db.query(model.Account).filter(model.Account.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        update_data = request.dict(exclude_unset=True)
        item.update(update_data, synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item.first()


def delete(db: Session, item_id):
    try:
        item = db.query(model.Account).filter(model.Account.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        item.delete(synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
