from pydantic import BaseModel
from typing import Optional


class AccountBase(BaseModel):
    name: str


class AccountCreate(AccountBase):
    email: str
    password: str


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class Account(AccountBase):
    id: int
    email: str
    password: str

    class Config:
        from_attributes = True
