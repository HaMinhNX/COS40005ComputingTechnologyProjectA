from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from models import User, Notification
from dependencies import get_current_user

router = APIRouter(
    prefix="/api/notifications",
    tags=["notifications"]
)

@router.get("/{user_id}")
async def get_notifications(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get notifications for a user"""
    notifications = db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(Notification.created_at.desc()).all()
    
    return notifications

@router.post("")
async def create_notification(data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new notification (used for appointment requests, etc.)"""
    notification = Notification(
        user_id=data.get("user_id"),
        title=data.get("title", "Thông báo mới"),
        message=data.get("message", ""),
        type=data.get("type", "info"),
        is_read=False
    )
    db.add(notification)
    try:
        db.commit()
        db.refresh(notification)
        return {"message": "Notification created", "notification_id": str(notification.notification_id)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{user_id}/read-all")
async def mark_all_read(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Mark all notifications as read"""
    db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).update({Notification.is_read: True})
    
    try:
        db.commit()
        return {"message": "All marked as read"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
