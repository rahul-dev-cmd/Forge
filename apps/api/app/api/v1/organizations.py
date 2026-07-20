import uuid
from typing import List
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import OrgRoleChecker
from app.models.user import User
from app.models.enums import OrganizationRole
from app.services.org_service import org_service, OrganizationCreate
from app.utils.response import wrap_response

router = APIRouter()

# Role guards dependencies
require_org_owner = OrgRoleChecker([OrganizationRole.OWNER])
require_org_admin = OrgRoleChecker([OrganizationRole.OWNER, OrganizationRole.ADMIN])
require_org_member = OrgRoleChecker([OrganizationRole.OWNER, OrganizationRole.ADMIN, OrganizationRole.MEMBER])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_in: OrganizationCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Initialize a new organization and make the creator the owner.
    """
    ip_addr = request.client.host if request.client else None
    org = await org_service.create_organization(db, org_in, owner_id=current_user.id, ip_address=ip_addr)
    return wrap_response(
        data={
            "id": str(org.id),
            "name": org.name,
            "slug": org.slug,
            "owner_id": str(org.owner_id)
        },
        message="Organization created successfully."
    )

@router.get("/{org_id}")
async def get_organization(
    org_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_org_member)
):
    """
    Retrieve organization metadata details.
    """
    org = await org_service.get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")
    return wrap_response(
        data={
            "id": str(org.id),
            "name": org.name,
            "slug": org.slug,
            "owner_id": str(org.owner_id),
            "created_at": org.created_at.isoformat()
        }
    )

@router.delete("/{org_id}")
async def delete_organization(
    org_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_org_owner)
):
    """
    Soft delete organization. Only the Owner can perform this action.
    """
    ip_addr = request.client.host if request.client else None
    org = await org_service.delete_organization(db, org_id, actor_id=current_user.id, ip_address=ip_addr)
    return wrap_response(
        data={"id": str(org.id), "deleted_at": org.deleted_at.isoformat()},
        message="Organization successfully deleted."
    )

@router.get("/{org_id}/members")
async def list_members(
    org_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_org_member)
):
    """
    List all memberships inside the organization.
    """
    memberships = await org_service.list_members(db, org_id)
    serialized = [
        {
            "id": str(m.id),
            "user_id": str(m.user_id),
            "role": m.role,
            "joined_at": m.joined_at.isoformat()
        } for m in memberships
    ]
    return wrap_response(data=serialized)

@router.patch("/{org_id}/members/{user_id}")
async def update_member_role(
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    role: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_org_admin)
):
    """
    Update member role inside the organization.
    """
    ip_addr = request.client.host if request.client else None
    membership = await org_service.update_member_role(
        db, org_id, target_user_id=user_id, new_role=role, actor_id=current_user.id, ip_address=ip_addr
    )
    return wrap_response(
        data={
            "id": str(membership.id),
            "user_id": str(membership.user_id),
            "role": membership.role
        },
        message="Member role updated successfully."
    )

@router.delete("/{org_id}/members/{user_id}")
async def remove_member(
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_org_admin)
):
    """
    Remove a member from organization membership.
    """
    ip_addr = request.client.host if request.client else None
    await org_service.remove_member(db, org_id, target_user_id=user_id, actor_id=current_user.id, ip_address=ip_addr)
    return wrap_response(data=None, message="Member removed successfully.")

@router.post("/{org_id}/leave")
async def leave_organization(
    org_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Leave organization membership.
    """
    ip_addr = request.client.host if request.client else None
    await org_service.leave_organization(db, org_id, user_id=current_user.id, ip_address=ip_addr)
    return wrap_response(data=None, message="Successfully left organization.")
