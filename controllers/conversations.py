from sqlalchemy.orm import Session
from models.conversations import Conversation, Message  # Only import what's necessary
from schemas import conversations as schema
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

def get_conversations_for_user(db: Session, user_id: str):
    try:
        result = db.query(Conversation).filter(
            (Conversation.participant_1 == user_id) | 
            (Conversation.participant_2 == user_id)
        ).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result

def create_conversation(db: Session, request: schema.ConversationCreate):
    new_conversation = Conversation(
        participant_1=request.participant_1,
        participant_2=request.participant_2,
        price=request.price  # Ensure 'price' is included
    )

    try:
        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_conversation

def add_message(db: Session, request: schema.MessageCreate):
    try:
        conversation = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found!")
        
        new_message = Message(
            conversation_id=request.conversation_id,
            sender=request.sender_id,  # Ensure sender uses 'sender' not 'sender_id' for consistency
            content=request.message_body
        )
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_message

def mark_as_read(db: Session, conversation_id: int, user_id: str):
    try:
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.sender != user_id,
            Message.is_read == False
        ).all()

        for message in messages:
            message.is_read = True

        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return {"message": "Messages marked as read"}

def get_conversation(db: Session, conversation_id: int):
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()

def delete_conversation(db: Session, conversation_id: int):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
    
    db.delete(conversation)
    db.commit()
    return {"detail": "Conversation deleted successfully."}

def get_message(db: Session, message_id: int):
    return db.query(Message).filter(Message.id == message_id).first()

def delete_message(db: Session, message_id: int):
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found.")
    
    db.delete(message)
    db.commit()
    return {"detail": "Message deleted successfully."}

def get_messages_for_conversation(db: Session, conversation_id: int):
    try:
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()
        
        if not messages:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No messages found in this conversation.")
        
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    return messages
