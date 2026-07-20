import uuid
from typing import List
from fastapi import APIRouter, Depends, Request, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.repository import repository_service, RepositoryCreate, RepositorySettingsUpdate
from app.utils.validators import validate_repo_url
from app.utils.response import wrap_response

router = APIRouter()

@router.get("")
async def list_repositories(
    project_id: uuid.UUID = Query(..., description="Target project ID filter"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List connected repositories in a project.
    """
    items = await repository_service.get_by_project(db, project_id)
    serialized = [
        {
            "id": str(r.id),
            "project_id": str(r.project_id),
            "workspace_id": str(r.workspace_id),
            "provider": r.provider,
            "external_id": r.external_id,
            "name": r.name,
            "default_branch": r.default_branch,
            "clone_url": r.clone_url,
            "visibility": r.visibility,
            "connection_status": r.connection_status
        } for r in items
    ]
    return wrap_response(data=serialized)

@router.post("", status_code=status.HTTP_201_CREATED)
async def connect_repository(
    repo_in: RepositoryCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Register and connect a Git repository metadata, validating the Git clone URL layout format.
    """
    # 1. Enforce repository clone URL matches regex rules
    validate_repo_url(repo_in.clone_url, repo_in.provider)

    ip_addr = request.client.host if request.client else None
    repo = await repository_service.create_repository(db, repo_in, actor_id=current_user.id, ip_address=ip_addr)
    return wrap_response(
        data={
            "id": str(repo.id),
            "name": repo.name,
            "provider": repo.provider,
            "clone_url": repo.clone_url
        },
        message="Repository connected successfully."
    )

@router.get("/{repository_id}")
async def get_repository_details(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve connected repository details by UUID.
    """
    repo = await repository_service.get_repository(db, repository_id)
    if not repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found.")
    return wrap_response(
        data={
            "id": str(repo.id),
            "project_id": str(repo.project_id),
            "workspace_id": str(repo.workspace_id),
            "provider": repo.provider,
            "name": repo.name,
            "default_branch": repo.default_branch,
            "clone_url": repo.clone_url,
            "visibility": repo.visibility,
            "connection_status": repo.connection_status
        }
    )

@router.patch("/{repository_id}/settings")
async def update_repository_settings(
    repository_id: uuid.UUID,
    settings_in: RepositorySettingsUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update connected repository settings.
    """
    ip_addr = request.client.host if request.client else None
    updated = await repository_service.update_settings(
        db, repository_id, settings_in, actor_id=current_user.id, ip_address=ip_addr
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository settings not found.")
    return wrap_response(
        data={
            "id": str(updated.id),
            "repository_id": str(updated.repository_id),
            "ai_enabled": updated.ai_enabled,
            "indexing_enabled": updated.indexing_enabled,
            "auto_sync": updated.auto_sync,
            "sync_interval": updated.sync_interval
        },
        message="Repository settings updated successfully."
    )
