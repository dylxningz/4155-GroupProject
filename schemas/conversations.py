from pydantic import BaseModel
from typing import List
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
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    participant_1: int
    participant_2: int
    item_id: int

class ConversationResponse(BaseModel):
    id: int
    participant_1: int
    participant_2: int
    item_id: int
    created_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True