from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from dependencies.database import get_db
from controllers import conversations as controller
from schemas import conversations as schema
from typing import List

router = APIRouter(
    prefix="/conversations",
    tags=['Conversations']
)

@router.post("/", response_model=schema.ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(request: schema.ConversationCreate, db: Session = Depends(get_db)):
    return controller.create_conversation(db, request)


@router.get("/", response_model=List[schema.ConversationResponse])
def get_conversations_for_user(user_id: int, db: Session = Depends(get_db)):
    return controller.get_conversations_for_user(db, user_id)


@router.post("/message", response_model=schema.MessageResponse, status_code=status.HTTP_201_CREATED)
def add_message(request: schema.MessageCreate, db: Session = Depends(get_db)):
    return controller.add_message(db, request)


@router.patch("/read/{conversation_id}", status_code=status.HTTP_200_OK)
def mark_as_read(conversation_id: int, user_id: int, db: Session = Depends(get_db)):
    return controller.mark_as_read(db, conversation_id, user_id)
