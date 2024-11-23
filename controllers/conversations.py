from sqlalchemy.orm import Session
from models.conversations import Conversation, Message
from schemas import conversations as schema
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

def get_conversations_for_item(db: Session, item_id: int):
    return db.query(Conversation).filter(Conversation.item_id == item_id).all()

def create_conversation(db: Session, request: schema.ConversationCreate):
    new_conversation = Conversation(
        participant_1=request.participant_1,
        participant_2=request.participant_2,
        item_id=request.item_id
    )
    try:
        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return new_conversation

def add_message(db: Session, request: schema.MessageCreate):
    new_message = Message(
        conversation_id=request.conversation_id,
        sender_id=request.sender_id,
        message_body=request.message_body
    )
    try:
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return new_message

def get_messages_for_conversation(db: Session, conversation_id: int):
    return db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
