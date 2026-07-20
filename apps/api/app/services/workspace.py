import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workspace import Workspace, WorkspaceMember
from app.models.audit_log import AuditLog
from app.models.enums import WorkspaceRole
from app.utils.rbac_hierarchy import (
    assert_can_assign_workspace_role,
    assert_can_manage_workspace_member,
)
from pydantic import BaseModel

class WorkspaceCreate(BaseModel):
    owner_id: uuid.UUID
    organization_id: uuid.UUID | None = None
    name: str
    slug: str
    description: str | None = None

class WorkspaceUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None

class WorkspaceService:
    async def create_workspace(self, db: AsyncSession, workspace_in: WorkspaceCreate, ip_address: str | None = None) -> Workspace:
        """
        Create a new workspace, validate name uniqueness, map creator as Owner, and audit log.
        """
        # 1. Enforce unique workspace slug for the owner
        slug_query = select(Workspace).filter(
            Workspace.owner_id == workspace_in.owner_id,
            Workspace.slug == workspace_in.slug,
            Workspace.deleted_at == None
        )
        slug_res = await db.execute(slug_query)
        if slug_res.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Workspace with slug '{workspace_in.slug}' already exists."
            )

        # 2. Enforce unique workspace name for the owner
        name_query = select(Workspace).filter(
            Workspace.owner_id == workspace_in.owner_id,
            Workspace.name == workspace_in.name,
            Workspace.deleted_at == None
        )
        name_res = await db.execute(name_query)
        if name_res.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Workspace with name '{workspace_in.name}' already exists."
            )

        workspace = Workspace(
            owner_id=workspace_in.owner_id,
            organization_id=workspace_in.organization_id,
            name=workspace_in.name,
            slug=workspace_in.slug,
            description=workspace_in.description
        )
        db.add(workspace)
        await db.commit()
        await db.refresh(workspace)

        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=workspace_in.owner_id,
            role=WorkspaceRole.OWNER.value
        )
        db.add(member)

        log = AuditLog(
            actor_id=workspace_in.owner_id,
            action="workspace_creation",
            target_type="workspace",
            target_id=workspace.id,
            details={"name": workspace.name, "slug": workspace.slug},
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()
        await db.refresh(workspace)
        return workspace

    async def get_workspace(self, db: AsyncSession, workspace_id: uuid.UUID) -> Workspace | None:
        query = select(Workspace).filter(Workspace.id == workspace_id, Workspace.deleted_at == None)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_slug(self, db: AsyncSession, slug: str) -> Workspace | None:
        query = select(Workspace).filter(Workspace.slug == slug, Workspace.deleted_at == None)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_owner(self, db: AsyncSession, owner_id: uuid.UUID) -> List[Workspace]:
        query = select(Workspace).filter(Workspace.owner_id == owner_id, Workspace.deleted_at == None)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def list_for_user(self, db: AsyncSession, user_id: uuid.UUID) -> List[tuple[Workspace, WorkspaceMember]]:
        """List active workspaces where the user is a member, with their membership row."""
        query = (
            select(Workspace, WorkspaceMember)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .filter(
                WorkspaceMember.user_id == user_id,
                Workspace.deleted_at == None,
            )
            .order_by(Workspace.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.all())

    async def add_member(
        self,
        db: AsyncSession,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str,
        actor_id: uuid.UUID,
        actor_role: str,
        ip_address: str | None = None,
    ) -> WorkspaceMember:
        assert_can_assign_workspace_role(actor_role, role)

        existing = await db.execute(
            select(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
        if existing.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this workspace.",
            )

        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user_id,
            role=role,
            invited_by=actor_id,
        )
        db.add(member)

        log = AuditLog(
            actor_id=actor_id,
            action="member_joined",
            target_type="workspace",
            target_id=workspace_id,
            details={"user_id": str(user_id), "role": role},
            ip_address=ip_address,
        )
        db.add(log)
        await db.commit()
        await db.refresh(member)
        return member

    async def update_member_role(
        self,
        db: AsyncSession,
        workspace_id: uuid.UUID,
        target_user_id: uuid.UUID,
        new_role: str,
        actor_id: uuid.UUID,
        actor_role: str,
        ip_address: str | None = None,
    ) -> WorkspaceMember:
        query = select(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == target_user_id,
        )
        result = await db.execute(query)
        membership = result.scalars().first()
        if not membership:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")

        assert_can_manage_workspace_member(actor_role, membership.role)

        if new_role == WorkspaceRole.OWNER.value:
            if actor_role != WorkspaceRole.OWNER.value:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the Owner can transfer ownership.",
                )
        else:
            assert_can_assign_workspace_role(actor_role, new_role)

        if (
            target_user_id == actor_id
            and membership.role == WorkspaceRole.OWNER.value
            and new_role != WorkspaceRole.OWNER.value
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Owner cannot demote themselves. Transfer ownership first.",
            )

        membership.role = new_role
        db.add(membership)

        log = AuditLog(
            actor_id=actor_id,
            action="role_changed",
            target_type="workspace",
            target_id=workspace_id,
            details={"user_id": str(target_user_id), "new_role": new_role},
            ip_address=ip_address,
        )
        db.add(log)
        await db.commit()
        await db.refresh(membership)
        return membership

    async def remove_member(
        self,
        db: AsyncSession,
        workspace_id: uuid.UUID,
        target_user_id: uuid.UUID,
        actor_id: uuid.UUID,
        actor_role: str,
        ip_address: str | None = None,
    ) -> None:
        if target_user_id == actor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove yourself. Use the leave endpoint instead.",
            )

        query = select(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == target_user_id,
        )
        result = await db.execute(query)
        membership = result.scalars().first()
        if not membership:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")

        assert_can_manage_workspace_member(actor_role, membership.role)

        await db.delete(membership)

        log = AuditLog(
            actor_id=actor_id,
            action="member_removed",
            target_type="workspace",
            target_id=workspace_id,
            details={"removed_user_id": str(target_user_id)},
            ip_address=ip_address,
        )
        db.add(log)
        await db.commit()

    async def update_workspace(
        self, db: AsyncSession, workspace_id: uuid.UUID, workspace_in: WorkspaceUpdate, actor_id: uuid.UUID, ip_address: str | None = None
    ) -> Workspace | None:
        workspace = await self.get_workspace(db, workspace_id)
        if not workspace:
            return None

        update_data = workspace_in.model_dump(exclude_unset=True)
        for field in update_data:
            if hasattr(workspace, field):
                setattr(workspace, field, update_data[field])

        db.add(workspace)

        log = AuditLog(
            actor_id=actor_id,
            action="workspace_update",
            target_type="workspace",
            target_id=workspace_id,
            details=update_data,
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()
        await db.refresh(workspace)
        return workspace

    async def delete_workspace(self, db: AsyncSession, workspace_id: uuid.UUID, actor_id: uuid.UUID, ip_address: str | None = None) -> Workspace | None:
        workspace = await self.get_workspace(db, workspace_id)
        if not workspace:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found.")

        if workspace.owner_id != actor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the Owner can delete this workspace."
            )

        workspace.deleted_at = datetime.now(timezone.utc)
        workspace.deleted_by = actor_id
        db.add(workspace)

        log = AuditLog(
            actor_id=actor_id,
            action="workspace_deletion",
            target_type="workspace",
            target_id=workspace_id,
            details={"name": workspace.name},
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()
        return workspace

workspace_service = WorkspaceService()
