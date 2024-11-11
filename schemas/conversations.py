from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MessageCreate(BaseModel):
    conversation_id: int
    sender_id: int
    message_body: str

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    message_body: str
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True


class ConversationCreate(BaseModel):
    participant_1: int
    participant_2: int
    price: float  # Add the price field to match your controller's logic


class ConversationResponse(BaseModel):
    id: int
    participant_1: int
    participant_2: int
    created_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        orm_mode = True
