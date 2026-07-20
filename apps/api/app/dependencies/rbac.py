import uuid
from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.enums import WorkspaceRole, OrganizationRole
from app.models.workspace import WorkspaceMember
from app.models.organization import OrganizationMembership
from app.models.project import Project

class WorkspaceRoleChecker:
    def __init__(self, allowed_roles: List[WorkspaceRole]):
        # Unpack enums to strings if needed
        self.allowed_roles = [r.value if hasattr(r, "value") else r for r in allowed_roles]

    async def __call__(
        self,
        workspace_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> WorkspaceMember:
        query = select(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id
        )
        result = await db.execute(query)
        membership = result.scalars().first()
        
        if not membership or membership.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Insufficient workspace permissions."
            )
        return membership

class OrgRoleChecker:
    def __init__(self, allowed_roles: List[OrganizationRole]):
        self.allowed_roles = [r.value if hasattr(r, "value") else r for r in allowed_roles]

    async def __call__(
        self,
        org_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> OrganizationMembership:
        query = select(OrganizationMembership).filter(
            OrganizationMembership.organization_id == org_id,
            OrganizationMembership.user_id == current_user.id
        )
        result = await db.execute(query)
        membership = result.scalars().first()
        
        if not membership or membership.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Insufficient organization permissions."
            )
        return membership

class ProjectWorkspaceRoleChecker:
    def __init__(self, allowed_roles: List[WorkspaceRole]):
        self.allowed_roles = [r.value if hasattr(r, "value") else r for r in allowed_roles]

    async def __call__(
        self,
        project_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> WorkspaceMember:
        # 1. Fetch project to resolve workspace association
        project_query = select(Project).filter(Project.id == project_id, Project.deleted_at == None)
        project_result = await db.execute(project_query)
        project = project_result.scalars().first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or has been deleted."
            )
            
        # 2. Verify workspace role
        query = select(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == project.workspace_id,
            WorkspaceMember.user_id == current_user.id
        )
        result = await db.execute(query)
        membership = result.scalars().first()
        
        if not membership or membership.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Insufficient workspace permissions for this project."
            )
        return membership
