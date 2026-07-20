import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserSettings
from app.repositories.user import user_repository, user_settings_repository
from app.repositories.audit_log import audit_log_repository
from app.models.audit_log import AuditLog
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    username: str | None = None
    full_name: str
    avatar_url: str | None = None
    clerk_id: str

class UserUpdate(BaseModel):
    full_name: str | None = None
    username: str | None = None
    avatar_url: str | None = None

class UserSettingsUpdate(BaseModel):
    theme: str | None = None
    language: str | None = None
    timezone: str | None = None
    preferred_ai_model: str | None = None

class UserService:
    async def get_or_create_user(self, db: AsyncSession, user_in: UserCreate, ip_address: str | None = None) -> User:
        """
        Lookup user by clerk_id. If missing, register them and initialize default UserSettings.
        """
        user = await user_repository.get_by_clerk_id(db, user_in.clerk_id)
        if not user:
            # Register user
            user = await user_repository.create(db, obj_in=user_in)
            
            # Initialize settings
            settings_obj = UserSettings(
                user_id=user.id,
                theme="system",
                language="en",
                timezone="UTC",
                preferred_ai_model="gpt-4o"
            )
            db.add(settings_obj)
            await db.commit()
            await db.refresh(user)

            # Audit log user registration/login
            log = AuditLog(
                actor_id=user.id,
                action="login",
                target_type="user",
                target_id=user.id,
                details={"message": "First login and registration synced from Clerk."},
                ip_address=ip_address
            )
            db.add(log)
            await db.commit()
        else:
            # Audit log user login
            log = AuditLog(
                actor_id=user.id,
                action="login",
                target_type="user",
                target_id=user.id,
                details={"message": "User session verified."},
                ip_address=ip_address
            )
            db.add(log)
            await db.commit()
            
        return user

    async def update_user(self, db: AsyncSession, user: User, user_in: UserUpdate) -> User:
        """
        Update user profile.
        """
        return await user_repository.update(db, db_obj=user, obj_in=user_in)

    async def get_settings(self, db: AsyncSession, user_id: uuid.UUID) -> UserSettings:
        """
        Fetch user settings. If missing, initialize defaults.
        """
        settings = await user_settings_repository.get_by_user_id(db, user_id)
        if not settings:
            settings = UserSettings(
                user_id=user_id,
                theme="system",
                language="en",
                timezone="UTC",
                preferred_ai_model="gpt-4o"
            )
            db.add(settings)
            await db.commit()
            await db.refresh(settings)
        return settings

    async def update_settings(self, db: AsyncSession, user_id: uuid.UUID, settings_in: UserSettingsUpdate, ip_address: str | None = None) -> UserSettings:
        """
        Update user settings and create an audit log.
        """
        settings = await self.get_settings(db, user_id)
        updated = await user_settings_repository.update(db, db_obj=settings, obj_in=settings_in)

        # Audit log settings modification
        log = AuditLog(
            actor_id=user_id,
            action="settings_change",
            target_type="settings",
            target_id=settings.id,
            details=settings_in.model_dump(exclude_unset=True),
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()
        
        return updated

user_service = UserService()
