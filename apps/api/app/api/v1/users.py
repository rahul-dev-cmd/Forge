from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.user import user_service, UserUpdate, UserSettingsUpdate
from app.schemas.user import UserResponse, UserSettings

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user authenticated profile.
    """
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update profile details.
    """
    return await user_service.update_user(db, db_obj=current_user, user_in=user_in)

@router.get("/me/settings", response_model=UserSettings)
async def get_my_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve settings preferences.
    """
    return await user_service.get_settings(db, current_user.id)

@router.patch("/me/settings", response_model=UserSettings)
async def update_my_settings(
    settings_in: UserSettingsUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update theme or language variables.
    """
    ip_addr = request.client.host if request.client else None
    return await user_service.update_settings(db, current_user.id, settings_in, ip_address=ip_addr)
