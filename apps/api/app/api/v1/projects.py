import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Request, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import WorkspaceRoleChecker, ProjectWorkspaceRoleChecker
from app.models.user import User
from app.models.enums import WorkspaceRole
from app.services.project import project_service, ProjectCreate, ProjectUpdate
from app.utils.response import wrap_response
from pydantic import BaseModel

router = APIRouter()

# Role checkers
require_workspace_viewer = WorkspaceRoleChecker([
    WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.MANAGER, WorkspaceRole.DEVELOPER, WorkspaceRole.VIEWER
])
require_workspace_manager = WorkspaceRoleChecker([WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.MANAGER])
require_project_manager = ProjectWorkspaceRoleChecker([WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.MANAGER])

class BulkArchiveRequest(BaseModel):
    project_ids: List[uuid.UUID]

@router.get("")
async def list_projects(
    workspace_id: uuid.UUID = Query(..., description="Target workspace ID filter"),
    query: Optional[str] = Query(None, description="Search query name/slug/desc"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by project status"),
    priority_filter: Optional[str] = Query(None, alias="priority", description="Filter by project priority"),
    favorite: Optional[bool] = Query(None, description="Filter only favorites"),
    sort_by: Optional[str] = Query("created_at", description="Sort by column"),
    order: str = Query("desc", description="Sort direction (asc/desc)"),
    page: int = Query(1, ge=1, description="Page number for offset pagination"),
    limit: int = Query(20, ge=1, le=100, description="Page limit size"),
    cursor: Optional[str] = Query(None, description="Cursor for cursor-based pagination"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_workspace_viewer)
):
    """
    List, filter, sort, search and paginate projects inside a workspace.
    Supports both cursor and offset pagination.
    """
    items, total, next_cursor = await project_service.query_projects(
        db,
        workspace_id,
        search_query=query,
        status_filter=status_filter,
        priority_filter=priority_filter,
        favorite_only=favorite,
        sort_by=sort_by,
        order=order,
        page=page,
        limit=limit,
        cursor=cursor
    )
    
    serialized = [
        {
            "id": str(p.id),
            "workspace_id": str(p.workspace_id),
            "owner_id": str(p.owner_id),
            "name": p.name,
            "slug": p.slug,
            "description": p.description,
            "status": p.status,
            "priority": p.priority,
            "tags": p.tags,
            "due_date": p.due_date.isoformat() if p.due_date else None,
            "visibility": p.visibility,
            "is_favorite": p.is_favorite,
            "version": p.version,
            "created_at": p.created_at.isoformat()
        } for p in items
    ]
    
    return wrap_response(
        data=serialized,
        page=page if not cursor else None,
        limit=limit,
        total=total,
        cursor=next_cursor
    )

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Initialize a new project within a workspace.
    """
    # Verify creator is a workspace Manager/Admin/Owner
    checker = WorkspaceRoleChecker([WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.MANAGER])
    await checker(project_in.workspace_id, current_user, db)

    if project_in.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create project with owner matching another user profile."
        )

    ip_addr = request.client.host if request.client else None
    project = await project_service.create_project(db, project_in, ip_address=ip_addr)
    return wrap_response(
        data={
            "id": str(project.id),
            "name": project.name,
            "slug": project.slug,
            "version": project.version
        },
        message="Project created successfully."
    )

@router.get("/{workspace_id}/{id_or_slug}")
async def get_project_details(
    workspace_id: uuid.UUID,
    id_or_slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_workspace_viewer)
):
    """
    Retrieve project details by UUID or Slug.
    """
    project = await project_service.get_project_by_id_or_slug(db, id_or_slug, workspace_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
        
    return wrap_response(
        data={
            "id": str(project.id),
            "workspace_id": str(project.workspace_id),
            "owner_id": str(project.owner_id),
            "name": project.name,
            "slug": project.slug,
            "description": project.description,
            "status": project.status,
            "priority": project.priority,
            "tags": project.tags,
            "due_date": project.due_date.isoformat() if project.due_date else None,
            "visibility": project.visibility,
            "is_favorite": project.is_favorite,
            "version": project.version,
            "created_at": project.created_at.isoformat()
        }
    )

@router.patch("/{project_id}")
async def update_project(
    project_id: uuid.UUID,
    project_in: ProjectUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_project_manager)
):
    """
    Update project details, applying concurrency version checking.
    """
    ip_addr = request.client.host if request.client else None
    updated = await project_service.update_project(
        db, project_id, project_in, actor_id=current_user.id, ip_address=ip_addr
    )
    return wrap_response(
        data={
            "id": str(updated.id),
            "name": updated.name,
            "version": updated.version
        },
        message="Project updated successfully."
    )

@router.post("/{project_id}/archive")
async def archive_project(
    project_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_project_manager)
):
    """
    Archive a project.
    """
    ip_addr = request.client.host if request.client else None
    archived = await project_service.archive_project(db, project_id, actor_id=current_user.id, ip_address=ip_addr)
    return wrap_response(
        data={"id": str(archived.id), "status": archived.status, "archived_at": archived.archived_at.isoformat()},
        message="Project archived successfully."
    )

@router.post("/{project_id}/restore")
async def restore_project(
    project_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_project_manager)
):
    """
    Restore an archived project back to active.
    """
    ip_addr = request.client.host if request.client else None
    restored = await project_service.restore_project(db, project_id, actor_id=current_user.id, ip_address=ip_addr)
    return wrap_response(
        data={"id": str(restored.id), "status": restored.status},
        message="Project restored successfully."
    )

@router.post("/bulk-archive")
async def bulk_archive(
    req: BulkArchiveRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Bulk archive multiple projects. Verified against workspace manager permissions for each project.
    """
    ip_addr = request.client.host if request.client else None
    
    # Pre-verify permissions for all target project workspaces
    for pid in req.project_ids:
        checker = ProjectWorkspaceRoleChecker([WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.MANAGER])
        await checker(pid, current_user, db)
        
    count = await project_service.bulk_archive_projects(
        db, req.project_ids, actor_id=current_user.id, ip_address=ip_addr
    )
    return wrap_response(data={"archived_count": count}, message=f"Successfully archived {count} projects.")

@router.delete("/{project_id}")
async def delete_project(
    project_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_project_manager)
):
    """
    Soft delete project.
    """
    ip_addr = request.client.host if request.client else None
    deleted = await project_service.delete_project(db, project_id, actor_id=current_user.id, ip_address=ip_addr)
    return wrap_response(
        data={"id": str(deleted.id), "deleted_at": deleted.deleted_at.isoformat()},
        message="Project deleted successfully."
    )
