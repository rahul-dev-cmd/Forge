from typing import Any, List
import uuid
from sqlalchemy import select, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.repositories.base import BaseRepository

class ProjectRepository(BaseRepository[Project, Any, Any]):
    def __init__(self):
        super().__init__(Project)

    async def get_by_workspace(
        self, db: AsyncSession, workspace_id: uuid.UUID, *, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        """
        Fetch all projects belonging to a specific workspace ID.
        """
        query = select(Project).filter(
            Project.workspace_id == workspace_id,
            Project.deleted_at == None
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_active_projects(
        self, db: AsyncSession, workspace_id: uuid.UUID, *, limit: int = 10
    ) -> List[Project]:
        """
        Fetch active projects (non-deleted) belonging to a specific workspace.
        """
        query = select(Project).filter(
            Project.workspace_id == workspace_id,
            Project.deleted_at == None
        ).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_recent_projects(
        self, db: AsyncSession, workspace_id: uuid.UUID, *, limit: int = 5
    ) -> List[Project]:
        """
        Fetch projects ordered by created date (newest first).
        """
        query = select(Project).filter(
            Project.workspace_id == workspace_id,
            Project.deleted_at == None
        ).order_by(desc(Project.created_at)).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def search_projects(
        self, db: AsyncSession, workspace_id: uuid.UUID, query_str: str, *, limit: int = 20
    ) -> List[Project]:
        """
        Perform a case-insensitive search by project name or description.
        """
        search_filter = f"%{query_str}%"
        query = select(Project).filter(
            Project.workspace_id == workspace_id,
            Project.deleted_at == None,
            or_(
                Project.name.ilike(search_filter),
                Project.description.ilike(search_filter)
            )
        ).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

project_repository = ProjectRepository()
