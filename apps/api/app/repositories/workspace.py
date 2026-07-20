from typing import Any, List
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workspace import Workspace, WorkspaceMember
from app.repositories.base import BaseRepository

class WorkspaceRepository(BaseRepository[Workspace, Any, Any]):
    def __init__(self):
        super().__init__(Workspace)

    async def get_by_owner(self, db: AsyncSession, owner_id: uuid.UUID) -> List[Workspace]:
        """
        Fetch workspaces owned by a user ID.
        """
        query = select(Workspace).filter(Workspace.owner_id == owner_id, Workspace.deleted_at == None)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_slug(self, db: AsyncSession, slug: str) -> Workspace | None:
        """
        Fetch workspace context by its routing slug.
        """
        query = select(Workspace).filter(Workspace.slug == slug, Workspace.deleted_at == None)
        result = await db.execute(query)
        return result.scalars().first()

class WorkspaceMemberRepository(BaseRepository[WorkspaceMember, Any, Any]):
    def __init__(self):
        super().__init__(WorkspaceMember)

    async def get_by_workspace(self, db: AsyncSession, workspace_id: uuid.UUID) -> List[WorkspaceMember]:
        """
        Fetch all members belonging to a workspace.
        """
        query = select(WorkspaceMember).filter(WorkspaceMember.workspace_id == workspace_id)
        result = await db.execute(query)
        return list(result.scalars().all())

workspace_repository = WorkspaceRepository()
workspace_member_repository = WorkspaceMemberRepository()
