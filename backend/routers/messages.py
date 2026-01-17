from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from models import User, Message
from dependencies import get_current_user
from schemas import MessageCreate, MessageResponse
from utils import paginate, Page
from fastapi import Query


router = APIRouter(
    prefix="/api/messages",
    tags=["messages"]
)

@router.get("/{user1_id}/{user2_id}", response_model=Page[MessageResponse])
async def get_conversation(
    user1_id: UUID, 
    user2_id: UUID, 
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Get conversation between two users with pagination"""
    query = db.query(Message).filter(
        ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
        ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
    ).order_by(Message.created_at.desc())
    
    return paginate(query, page, size)


@router.get("/{user_id}", response_model=Page[MessageResponse])
async def get_user_messages(
    user_id: UUID, 
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Get all messages for a user with pagination"""
    query = db.query(Message).filter(
        (Message.sender_id == user_id) | (Message.receiver_id == user_id)
    ).order_by(Message.created_at.desc())
    
    return paginate(query, page, size)


@router.post("", response_model=MessageResponse)
async def send_message(data: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Send a message"""
    try:
        new_message = Message(
            sender_id=current_user.user_id,
            receiver_id=data.receiver_id,
            content=data.content
        )
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        return new_message
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

