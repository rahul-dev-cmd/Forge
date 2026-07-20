import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.notification import notification_repository
from app.schemas.notification import NotificationResponse

router = APIRouter()

@router.get("", response_model=List[NotificationResponse])
async def list_notifications(
    unread_only: bool = Query(False, description="Filter list to show only unread notifications"),
    skip: int = Query(0, description="Offset for pagination"),
    limit: int = Query(100, description="Page size limit"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Query system notifications list for authenticated user.
    """
    return await notification_repository.get_by_user(
        db, current_user.id, unread_only=unread_only, skip=skip, limit=limit
    )

@router.post("/read-all", response_model=dict)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark all unread notifications for active user session as read.
    """
    count = await notification_repository.mark_all_read(db, current_user.id)
    return {"message": f"Successfully marked {count} notifications as read."}

@router.patch("/{notification_id}", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: uuid.UUID,
    is_read: bool = Query(True, description="Target read status toggle"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a single notification read status.
    """
    notif = await notification_repository.get(db, notification_id)
    if not notif or notif.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found for this user account context."
        )
        
    updated = await notification_repository.update(db, db_obj=notif, obj_in={"is_read": is_read})
    return updated
