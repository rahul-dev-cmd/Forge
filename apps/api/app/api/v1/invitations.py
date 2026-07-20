import uuid
from typing import List
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import OrgRoleChecker
from app.models.user import User
from app.models.enums import OrganizationRole
from app.services.invitation_service import invitation_service, InvitationCreate
from app.utils.response import wrap_response
from pydantic import BaseModel

router = APIRouter()

# Role guard for inviting members
require_org_admin = OrgRoleChecker([OrganizationRole.OWNER, OrganizationRole.ADMIN])

class TokenRequest(BaseModel):
    token: str

@router.post("/organizations/{org_id}/invitations", status_code=status.HTTP_201_CREATED)
async def invite_member(
    org_id: uuid.UUID,
    invite_in: InvitationCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_org_admin)
):
    """
    Invite a member to the organization by generating a secure invite token.
    """
    ip_addr = request.client.host if request.client else None
    inv = await invitation_service.create_invitation(
        db, org_id, invite_in, actor_id=current_user.id, ip_address=ip_addr
    )
    return wrap_response(
        data={
            "id": str(inv.id),
            "email": inv.email,
            "role": inv.role,
            "token": inv.token, # Return token to send in email link
            "expires_at": inv.expires_at.isoformat()
        },
        message="Invitation sent successfully."
    )

@router.get("/organizations/{org_id}/invitations")
async def list_pending_invitations(
    org_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_org_admin)
):
    """
    List pending invitations inside the organization.
    """
    invitations = await invitation_service.list_pending_invitations(db, org_id)
    serialized = [
        {
            "id": str(i.id),
            "email": i.email,
            "role": i.role,
            "expires_at": i.expires_at.isoformat()
        } for i in invitations
    ]
    return wrap_response(data=serialized)

@router.post("/accept")
async def accept_invitation(
    req: TokenRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Accept organization invitation using the secure random token.
    """
    ip_addr = request.client.host if request.client else None
    membership = await invitation_service.accept_invitation(
        db, token=req.token, user_id=current_user.id, ip_address=ip_addr
    )
    return wrap_response(
        data={
            "id": str(membership.id),
            "organization_id": str(membership.organization_id),
            "role": membership.role
        },
        message="Invitation accepted successfully. You joined the organization."
    )

@router.post("/reject")
async def reject_invitation(
    req: TokenRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reject organization invitation using the secure token.
    """
    ip_addr = request.client.host if request.client else None
    await invitation_service.reject_invitation(
        db, token=req.token, user_id=current_user.id, ip_address=ip_addr
    )
    return wrap_response(data=None, message="Invitation rejected.")
