from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies.database import get_db
from controllers import conversations as controller
from schemas import conversations as schema
from typing import List

router = APIRouter(
    prefix="/conversations",
    tags=['Conversations']
)


@router.get("/conversations")
def get_user_conversations(user_id: int, db: Session = Depends(get_db)):
    return controller.get_conversations_for_user(db, user_id)

@router.post("/", response_model=schema.ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(request: schema.ConversationCreate, db: Session = Depends(get_db)):
    return controller.create_conversation(db, request)


@router.get("/", response_model=List[schema.ConversationResponse])
def get_conversations_for_user(user_id: int, db: Session = Depends(get_db)):
    return controller.get_conversations_for_user(db, user_id)

# Ensure this function is defined in your controller instead
# Remove this from the router file if already defined in the controller
def get_conversations_for_user(db: Session, user_id: int):
    conversations = db.query(ConversationModel).filter(
        ConversationModel.user_id == user_id  # Adjust this according to your model structure
    ).all()
    return conversations


@router.post("/message", response_model=schema.MessageResponse, status_code=status.HTTP_201_CREATED)
def add_message(request: schema.MessageCreate, db: Session = Depends(get_db)):
    return controller.add_message(db, request)


@router.patch("/read/{conversation_id}", status_code=status.HTTP_200_OK)
def mark_as_read(conversation_id: int, user_id: int, db: Session = Depends(get_db)):
    return controller.mark_as_read(db, conversation_id, user_id)
# Add DELETE Endpoints

@router.delete("/{conversation_id}", status_code=status.HTTP_200_OK)
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conversation = controller.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    controller.delete_conversation(db, conversation_id)
    return {"detail": "Conversation deleted successfully"}

@router.delete("/message/{message_id}", status_code=status.HTTP_200_OK)
def delete_message(message_id: int, db: Session = Depends(get_db)):
    message = controller.get_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    controller.delete_message(db, message_id)
    return {"detail": "Message deleted successfully"}

@router.get("/{conversation_id}/messages", response_model=List[schema.MessageResponse])
def get_messages(conversation_id: int, db: Session = Depends(get_db)):
    messages = controller.get_messages_for_conversation(db, conversation_id)
    if not messages:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No messages found.")
    return messages