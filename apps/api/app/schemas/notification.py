from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class NotificationBase(BaseModel):
    title: str
    message: str
    type: str

class NotificationCreate(NotificationBase):
    user_id: UUID

class NotificationResponse(NotificationBase):
    id: UUID
    user_id: UUID
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
