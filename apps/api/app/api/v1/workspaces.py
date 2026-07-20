import uuid
from typing import List
from fastapi import APIRouter, Depends, Request, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import WorkspaceRoleChecker
from app.models.user import User
from app.models.workspace import WorkspaceMember
from app.models.enums import WorkspaceRole
from app.services.workspace import workspace_service, WorkspaceCreate, WorkspaceUpdate
from app.utils.response import wrap_response

router = APIRouter()

# Role guards
require_workspace_owner = WorkspaceRoleChecker([WorkspaceRole.OWNER])
require_workspace_admin = WorkspaceRoleChecker([WorkspaceRole.OWNER, WorkspaceRole.ADMIN])
require_workspace_member = WorkspaceRoleChecker([
    WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.MANAGER,
    WorkspaceRole.DEVELOPER, WorkspaceRole.VIEWER
])


@router.get("")
async def list_my_workspaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List workspaces where the authenticated user is a member.
    """
    rows = await workspace_service.list_for_user(db, current_user.id)
    serialized = [
        {
            "id": str(w.id),
            "name": w.name,
            "slug": w.slug,
            "description": w.description,
            "owner_id": str(w.owner_id),
            "organization_id": str(w.organization_id) if w.organization_id else None,
            "role": m.role,
            "created_at": w.created_at.isoformat()
        } for w, m in rows
    ]
    return wrap_response(data=serialized)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_in: WorkspaceCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Initialize a new workspace.
    """
    if workspace_in.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create workspace for another user account."
        )
    ip_addr = request.client.host if request.client else None
    workspace = await workspace_service.create_workspace(db, workspace_in, ip_address=ip_addr)
    return wrap_response(
        data={
            "id": str(workspace.id),
            "name": workspace.name,
            "slug": workspace.slug,
            "owner_id": str(workspace.owner_id)
        },
        message="Workspace created successfully."
    )


@router.get("/{workspace_id}")
async def get_workspace(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_workspace_member)
):
    """
    Retrieve workspace details by UUID.
    """
    workspace = await workspace_service.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found.")
    return wrap_response(
        data={
            "id": str(workspace.id),
            "name": workspace.name,
            "slug": workspace.slug,
            "description": workspace.description,
            "owner_id": str(workspace.owner_id),
            "organization_id": str(workspace.organization_id) if workspace.organization_id else None,
            "created_at": workspace.created_at.isoformat()
        }
    )


@router.patch("/{workspace_id}")
async def update_workspace(
    workspace_id: uuid.UUID,
    workspace_in: WorkspaceUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_workspace_admin)
):
    """
    Update active workspace metadata. Requires Admin or Owner role.
    """
    ip_addr = request.client.host if request.client else None
    updated = await workspace_service.update_workspace(
        db, workspace_id, workspace_in, actor_id=current_user.id, ip_address=ip_addr
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found.")
    return wrap_response(
        data={
            "id": str(updated.id),
            "name": updated.name,
            "slug": updated.slug
        },
        message="Workspace updated successfully."
    )


@router.delete("/{workspace_id}")
async def delete_workspace(
    workspace_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_workspace_owner)
):
    """
    Soft delete workspace. Only the Owner can perform this action.
    """
    ip_addr = request.client.host if request.client else None
    workspace = await workspace_service.delete_workspace(
        db, workspace_id, actor_id=current_user.id, ip_address=ip_addr
    )
    return wrap_response(
        data={"id": str(workspace.id), "deleted_at": workspace.deleted_at.isoformat()},
        message="Workspace deleted successfully."
    )


# --- Workspace Members Management ---

@router.get("/{workspace_id}/members")
async def list_workspace_members(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_workspace_member)
):
    """
    List all members in a workspace.
    """
    query = select(WorkspaceMember).filter(WorkspaceMember.workspace_id == workspace_id)
    result = await db.execute(query)
    members = list(result.scalars().all())
    serialized = [
        {
            "id": str(m.id),
            "user_id": str(m.user_id),
            "workspace_id": str(m.workspace_id),
            "role": m.role,
            "invited_by": str(m.invited_by) if m.invited_by else None,
            "joined_at": m.joined_at.isoformat()
        } for m in members
    ]
    return wrap_response(data=serialized)


@router.post("/{workspace_id}/members", status_code=status.HTTP_201_CREATED)
async def add_workspace_member(
    workspace_id: uuid.UUID,
    user_id: uuid.UUID = Query(..., description="User ID to add"),
    role: str = Query(WorkspaceRole.DEVELOPER.value, description="Role to assign"),
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMember = Depends(require_workspace_admin)
):
    """
    Add a member to the workspace. Requires Admin or Owner role.
    """
    ip_addr = request.client.host if request and request.client else None
    member = await workspace_service.add_member(
        db,
        workspace_id=workspace_id,
        user_id=user_id,
        role=role,
        actor_id=current_user.id,
        actor_role=membership.role,
        ip_address=ip_addr,
    )
    return wrap_response(
        data={
            "id": str(member.id),
            "user_id": str(member.user_id),
            "role": member.role
        },
        message="Member added successfully."
    )


@router.patch("/{workspace_id}/members/{member_user_id}")
async def update_workspace_member_role(
    workspace_id: uuid.UUID,
    member_user_id: uuid.UUID,
    role: str = Query(..., description="New role to assign"),
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMember = Depends(require_workspace_admin)
):
    """
    Update a workspace member's role with hierarchy enforcement.
    """
    ip_addr = request.client.host if request and request.client else None
    updated = await workspace_service.update_member_role(
        db,
        workspace_id=workspace_id,
        target_user_id=member_user_id,
        new_role=role,
        actor_id=current_user.id,
        actor_role=membership.role,
        ip_address=ip_addr,
    )
    return wrap_response(
        data={
            "id": str(updated.id),
            "user_id": str(updated.user_id),
            "role": updated.role
        },
        message="Member role updated successfully."
    )


@router.delete("/{workspace_id}/members/{member_user_id}")
async def remove_workspace_member(
    workspace_id: uuid.UUID,
    member_user_id: uuid.UUID,
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    membership: WorkspaceMember = Depends(require_workspace_admin)
):
    """
    Remove a member from the workspace with hierarchy enforcement.
    """
    ip_addr = request.client.host if request and request.client else None
    await workspace_service.remove_member(
        db,
        workspace_id=workspace_id,
        target_user_id=member_user_id,
        actor_id=current_user.id,
        actor_role=membership.role,
        ip_address=ip_addr,
    )
    return wrap_response(data=None, message="Member removed successfully.")
