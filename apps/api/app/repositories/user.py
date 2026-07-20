from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserSettings
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User, Any, Any]):
    def __init__(self):
        super().__init__(User)

    async def get_by_clerk_id(self, db: AsyncSession, clerk_id: str) -> User | None:
        """
        Lookup a user profile directly by Clerk Identity ID.
        """
        query = select(User).filter(User.clerk_id == clerk_id, User.deleted_at == None)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """
        Lookup a user profile directly by email.
        """
        query = select(User).filter(User.email == email, User.deleted_at == None)
        result = await db.execute(query)
        return result.scalars().first()

class UserSettingsRepository(BaseRepository[UserSettings, Any, Any]):
    def __init__(self):
        super().__init__(UserSettings)

    async def get_by_user_id(self, db: AsyncSession, user_id: str) -> UserSettings | None:
        """
        Lookup user preferences settings by user UUID.
        """
        query = select(UserSettings).filter(UserSettings.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().first()

user_repository = UserRepository()
user_settings_repository = UserSettingsRepository()
