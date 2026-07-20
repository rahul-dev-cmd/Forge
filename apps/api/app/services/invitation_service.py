import uuid
import secrets
from datetime import datetime, timezone, timedelta
from typing import List
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.invitation import OrganizationInvitation
from app.models.organization import OrganizationMembership
from app.models.enums import InvitationStatus, OrganizationRole
from app.models.audit_log import AuditLog
from app.utils.rbac_hierarchy import assert_can_assign_org_role
from pydantic import BaseModel, EmailStr


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _is_expired(expires_at: datetime) -> bool:
    """Compare expiry safely against SQLite naive and Postgres aware datetimes."""
    now = _utc_now()
    if expires_at.tzinfo is None:
        now = now.replace(tzinfo=None)
    return expires_at < now


class InvitationCreate(BaseModel):
    email: EmailStr
    role: str = OrganizationRole.MEMBER.value

class InvitationService:
    async def create_invitation(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        invite_in: InvitationCreate,
        actor_id: uuid.UUID,
        ip_address: str | None = None
    ) -> OrganizationInvitation:
        """
        Create a secure organization membership invitation with a unique token valid for 7 days.
        """
        # Validate that the role is supported
        if invite_in.role not in [r.value for r in OrganizationRole]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid organization role: '{invite_in.role}'."
            )

        # Hierarchy: inviter cannot invite at equal or higher rank than themselves
        actor_query = select(OrganizationMembership).filter(
            OrganizationMembership.organization_id == org_id,
            OrganizationMembership.user_id == actor_id,
        )
        actor_res = await db.execute(actor_query)
        actor_membership = actor_res.scalars().first()
        if not actor_membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization.",
            )
        assert_can_assign_org_role(actor_membership.role, invite_in.role)

        # 1. Prevent duplicate pending invitations for same email
        dup_query = select(OrganizationInvitation).filter(
            OrganizationInvitation.organization_id == org_id,
            OrganizationInvitation.email == invite_in.email,
            OrganizationInvitation.status == InvitationStatus.PENDING.value,
        )
        dup_res = await db.execute(dup_query)
        for pending in dup_res.scalars().all():
            if not _is_expired(pending.expires_at):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"An active invitation for '{invite_in.email}' is already pending."
                )

        # 2. Check if user is already a member
        # Find user by email first
        from app.models.user import User
        user_query = select(User).filter(User.email == invite_in.email)
        user_res = await db.execute(user_query)
        user = user_res.scalars().first()
        if user:
            mem_query = select(OrganizationMembership).filter(
                OrganizationMembership.organization_id == org_id,
                OrganizationMembership.user_id == user.id
            )
            mem_res = await db.execute(mem_query)
            if mem_res.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with email '{invite_in.email}' is already a member of this organization."
                )

        # 3. Generate a secure URL-safe token
        token = secrets.token_urlsafe(32)
        expires_at = _utc_now() + timedelta(days=7)

        invitation = OrganizationInvitation(
            organization_id=org_id,
            email=invite_in.email,
            role=invite_in.role,
            invited_by=actor_id,
            status=InvitationStatus.PENDING.value,
            token=token,
            expires_at=expires_at
        )

        db.add(invitation)

        # Log audit trail
        log = AuditLog(
            actor_id=actor_id,
            action="member_invited",
            target_type="invitation",
            target_id=org_id, # Target org
            details={"email": invite_in.email, "role": invite_in.role},
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()
        await db.refresh(invitation)
        return invitation

    async def list_pending_invitations(self, db: AsyncSession, org_id: uuid.UUID) -> List[OrganizationInvitation]:
        """
        List all pending and active invitations inside an organization.
        """
        query = select(OrganizationInvitation).filter(
            OrganizationInvitation.organization_id == org_id,
            OrganizationInvitation.status == InvitationStatus.PENDING.value,
        )
        result = await db.execute(query)
        return [inv for inv in result.scalars().all() if not _is_expired(inv.expires_at)]

    async def accept_invitation(
        self, db: AsyncSession, token: str, user_id: uuid.UUID, ip_address: str | None = None
    ) -> OrganizationMembership:
        """
        Accept an invitation using the secure unique token.
        """
        query = select(OrganizationInvitation).filter(OrganizationInvitation.token == token)
        res = await db.execute(query)
        inv = res.scalars().first()
        if not inv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation link not found or invalid."
            )

        if inv.status != InvitationStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invitation has already been {inv.status}."
            )

        if _is_expired(inv.expires_at):
            inv.status = InvitationStatus.EXPIRED.value
            db.add(inv)
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation link has expired."
            )

        # Retrieve user email compatibility validation
        from app.models.user import User
        user = await db.get(User, user_id)
        if not user or user.email != inv.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This invitation was sent to a different email address."
            )

        # Mark invitation accepted
        inv.status = InvitationStatus.ACCEPTED.value
        db.add(inv)

        # Add user to organization membership list
        membership = OrganizationMembership(
            organization_id=inv.organization_id,
            user_id=user_id,
            role=inv.role
        )
        db.add(membership)

        # Log audit trail
        log = AuditLog(
            actor_id=user_id,
            action="member_joined",
            target_type="organization",
            target_id=inv.organization_id,
            details={"email": inv.email, "role": inv.role},
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()
        await db.refresh(membership)
        return membership

    async def reject_invitation(
        self, db: AsyncSession, token: str, user_id: uuid.UUID, ip_address: str | None = None
    ) -> None:
        """
        Reject an invitation.
        """
        query = select(OrganizationInvitation).filter(OrganizationInvitation.token == token)
        res = await db.execute(query)
        inv = res.scalars().first()
        if not inv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found.")

        if inv.status != InvitationStatus.PENDING.value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation already resolved.")

        # Validate matching user
        from app.models.user import User
        user = await db.get(User, user_id)
        if not user or user.email != inv.email:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot reject another user's invitation.")

        inv.status = InvitationStatus.REJECTED.value
        db.add(inv)

        # Log audit trail
        log = AuditLog(
            actor_id=user_id,
            action="invitation_rejected",
            target_type="invitation",
            target_id=inv.id,
            details={"email": inv.email},
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()

invitation_service = InvitationService()
