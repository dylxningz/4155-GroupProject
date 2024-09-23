from sqlalchemy.orm import Session
from models import conversations as model
from schemas import conversations as schema
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError


def create_conversation(db: Session, request: schema.ConversationCreate):
    new_conversation = model.Conversation(
        participant_1=request.participant_1,
        participant_2=request.participant_2
    )

    try:
        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_conversation


def get_conversations_for_user(db: Session, user_id: int):
    try:
        result = db.query(model.Conversation).filter(
            (model.Conversation.participant_1 == user_id) | 
            (model.Conversation.participant_2 == user_id)
        ).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result


def add_message(db: Session, request: schema.MessageCreate):
    try:
        conversation = db.query(model.Conversation).filter(model.Conversation.id == request.conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found!")
        
        new_message = model.Message(
            conversation_id=request.conversation_id,
            sender_id=request.sender_id,
            message_body=request.message_body
        )
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_message


def mark_as_read(db: Session, conversation_id: int, user_id: int):
    try:
        messages = db.query(model.Message).filter(
            model.Message.conversation_id == conversation_id,
            model.Message.sender_id != user_id,
            model.Message.is_read == False
        ).all()

        for message in messages:
            message.is_read = True

        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return {"message": "Messages marked as read"}
