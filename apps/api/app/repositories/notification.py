from typing import Any, List
import uuid
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification
from app.repositories.base import BaseRepository

class NotificationRepository(BaseRepository[Notification, Any, Any]):
    def __init__(self):
        super().__init__(Notification)

    async def get_by_user(
        self, db: AsyncSession, user_id: uuid.UUID, *, unread_only: bool = False, skip: int = 0, limit: int = 100
    ) -> List[Notification]:
        """
        Fetch notifications for a user, optionally filtering by unread status.
        """
        query = select(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.is_read == False)
        query = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def mark_all_read(self, db: AsyncSession, user_id: uuid.UUID) -> int:
        """
        Mark all notifications for a user as read.
        """
        query = select(Notification).filter(Notification.user_id == user_id, Notification.is_read == False)
        result = await db.execute(query)
        unread_notifications = result.scalars().all()
        for notif in unread_notifications:
            notif.is_read = True
            db.add(notif)
        if unread_notifications:
            await db.commit()
        return len(unread_notifications)

notification_repository = NotificationRepository()
