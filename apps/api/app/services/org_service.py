import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.organization import Organization, OrganizationMembership
from app.models.enums import OrganizationRole
from app.models.audit_log import AuditLog
from app.models.workspace import Workspace
from app.utils.rbac_hierarchy import (
    assert_can_assign_org_role,
    assert_can_manage_org_member,
    organization_role_rank,
)
from pydantic import BaseModel

class OrganizationCreate(BaseModel):
    name: str
    slug: str

class OrgService:
    async def create_organization(
        self, db: AsyncSession, org_in: OrganizationCreate, owner_id: uuid.UUID, ip_address: str | None = None
    ) -> Organization:
        """
        Create an organization, register the creator as Owner, and audit the creation.
        """
        # Validate unique slug
        slug_check = await db.execute(select(Organization).filter(Organization.slug == org_in.slug))
        if slug_check.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization with slug '{org_in.slug}' already exists."
            )

        # Create Organization
        org = Organization(
            name=org_in.name,
            slug=org_in.slug,
            owner_id=owner_id
        )
        db.add(org)
        await db.commit()
        await db.refresh(org)

        # Add creator as Owner member
        membership = OrganizationMembership(
            organization_id=org.id,
            user_id=owner_id,
            role=OrganizationRole.OWNER.value
        )
        db.add(membership)
        
        # Log audit trail
        log = AuditLog(
            actor_id=owner_id,
            action="organization_creation",
            target_type="organization",
            target_id=org.id,
            details={"name": org.name, "slug": org.slug},
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()
        await db.refresh(org)
        return org

    async def get_organization(self, db: AsyncSession, org_id: uuid.UUID) -> Organization | None:
        """
        Fetch organization by ID, filtering out soft-deleted ones.
        """
        query = select(Organization).filter(Organization.id == org_id, Organization.deleted_at == None)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_slug(self, db: AsyncSession, slug: str) -> Organization | None:
        """
        Fetch organization by Slug, filtering out soft-deleted ones.
        """
        query = select(Organization).filter(Organization.slug == slug, Organization.deleted_at == None)
        result = await db.execute(query)
        return result.scalars().first()

    async def list_members(self, db: AsyncSession, org_id: uuid.UUID) -> List[OrganizationMembership]:
        """
        List all memberships in an organization.
        """
        query = select(OrganizationMembership).filter(OrganizationMembership.organization_id == org_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def update_member_role(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        target_user_id: uuid.UUID,
        new_role: str,
        actor_id: uuid.UUID,
        ip_address: str | None = None
    ) -> OrganizationMembership:
        """
        Update a member's role inside the organization with strict RBAC boundary checks.
        """
        # 1. Fetch actor's role
        actor_query = select(OrganizationMembership).filter(
            OrganizationMembership.organization_id == org_id,
            OrganizationMembership.user_id == actor_id
        )
        actor_res = await db.execute(actor_query)
        actor_membership = actor_res.scalars().first()
        if not actor_membership or actor_membership.role not in [OrganizationRole.OWNER.value, OrganizationRole.ADMIN.value]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Owners and Admins can modify member roles."
            )

        # 2. Fetch target member
        target_query = select(OrganizationMembership).filter(
            OrganizationMembership.organization_id == org_id,
            OrganizationMembership.user_id == target_user_id
        )
        target_res = await db.execute(target_query)
        target_membership = target_res.scalars().first()
        if not target_membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target user membership not found."
            )

        # 3. Hierarchy: cannot manage equal/higher members, cannot assign equal/higher roles
        assert_can_manage_org_member(actor_membership.role, target_membership.role)

        # Ownership transfer is Owner-only and must go through an explicit equal-rank exception
        if new_role == OrganizationRole.OWNER.value:
            if actor_membership.role != OrganizationRole.OWNER.value:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the Owner can transfer ownership.",
                )
        else:
            assert_can_assign_org_role(actor_membership.role, new_role)

        # Prevent accidental demotion of self below Owner without transferring first
        if target_user_id == actor_id and organization_role_rank(new_role) < organization_role_rank(
            OrganizationRole.OWNER.value
        ):
            if actor_membership.role == OrganizationRole.OWNER.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Owner cannot demote themselves. Transfer ownership first.",
                )

        target_membership.role = new_role
        db.add(target_membership)

        # Log audit trail
        log = AuditLog(
            actor_id=actor_id,
            action="role_changed",
            target_type="organization_membership",
            target_id=target_user_id,
            details={"new_role": new_role},
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()
        await db.refresh(target_membership)
        return target_membership

    async def remove_member(
        self, db: AsyncSession, org_id: uuid.UUID, target_user_id: uuid.UUID, actor_id: uuid.UUID, ip_address: str | None = None
    ) -> None:
        """
        Remove a member from the organization.
        """
        if target_user_id == actor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove yourself from organization. Use leave endpoint instead."
            )

        # Fetch actor role
        actor_query = select(OrganizationMembership).filter(
            OrganizationMembership.organization_id == org_id,
            OrganizationMembership.user_id == actor_id
        )
        actor_res = await db.execute(actor_query)
        actor_mem = actor_res.scalars().first()
        if not actor_mem or actor_mem.role not in [OrganizationRole.OWNER.value, OrganizationRole.ADMIN.value]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Owners and Admins can remove members."
            )

        # Fetch target member
        target_query = select(OrganizationMembership).filter(
            OrganizationMembership.organization_id == org_id,
            OrganizationMembership.user_id == target_user_id
        )
        target_res = await db.execute(target_query)
        target_mem = target_res.scalars().first()
        if not target_mem:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")

        assert_can_manage_org_member(actor_mem.role, target_mem.role)

        await db.delete(target_mem)

        # Log audit trail
        log = AuditLog(
            actor_id=actor_id,
            action="member_removed",
            target_type="organization",
            target_id=org_id,
            details={"removed_user_id": str(target_user_id)},
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()

    async def leave_organization(self, db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, ip_address: str | None = None) -> None:
        """
        Leave organization membership.
        """
        # Fetch membership
        query = select(OrganizationMembership).filter(
            OrganizationMembership.organization_id == org_id,
            OrganizationMembership.user_id == user_id
        )
        res = await db.execute(query)
        mem = res.scalars().first()
        if not mem:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found.")

        # Guard: Owner cannot leave without transferring ownership first
        if mem.role == OrganizationRole.OWNER.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Owner cannot leave organization. Please transfer ownership to another user first."
            )

        await db.delete(mem)

        # Log audit trail
        log = AuditLog(
            actor_id=user_id,
            action="member_left",
            target_type="organization",
            target_id=org_id,
            details={"user_id": str(user_id)},
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()

    async def delete_organization(self, db: AsyncSession, org_id: uuid.UUID, actor_id: uuid.UUID, ip_address: str | None = None) -> Organization:
        """
        Soft delete the organization (Owner only) along with workspaces.
        """
        org = await self.get_organization(db, org_id)
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")

        if org.owner_id != actor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the Owner can delete the organization."
            )

        # Soft Delete Organization
        org.deleted_at = datetime.now(timezone.utc)
        org.deleted_by = actor_id
        db.add(org)

        # Soft Delete Workspaces in Org
        ws_query = select(Workspace).filter(Workspace.organization_id == org_id, Workspace.deleted_at == None)
        ws_res = await db.execute(ws_query)
        for ws in ws_res.scalars().all():
            ws.deleted_at = datetime.now(timezone.utc)
            ws.deleted_by = actor_id
            db.add(ws)

        # Log audit trail
        log = AuditLog(
            actor_id=actor_id,
            action="organization_deletion",
            target_type="organization",
            target_id=org_id,
            details={"name": org.name},
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()
        return org

org_service = OrgService()
