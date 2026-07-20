from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

class UserSettingsBase(BaseModel):
    theme: str
    language: str
    timezone: str
    preferred_ai_model: str

class UserSettingsUpdate(BaseModel):
    theme: str | None = None
    language: str | None = None
    timezone: str | None = None
    preferred_ai_model: str | None = None

class UserSettings(UserSettingsBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: str
    username: str | None = None
    full_name: str
    avatar_url: str | None = None

class UserCreate(UserBase):
    clerk_id: str

class UserUpdate(BaseModel):
    full_name: str | None = None
    username: str | None = None
    avatar_url: str | None = None

class UserResponse(UserBase):
    id: UUID
    clerk_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
