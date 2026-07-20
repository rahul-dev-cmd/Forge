from typing import Any, List
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.repository import Repository, RepositorySettings
from app.repositories.base import BaseRepository

class RepositoryRepository(BaseRepository[Repository, Any, Any]):
    def __init__(self):
        super().__init__(Repository)

    async def get_by_project(self, db: AsyncSession, project_id: uuid.UUID) -> List[Repository]:
        """
        Fetch all connected Git repositories associated with a project ID.
        """
        query = select(Repository).filter(Repository.project_id == project_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_external_id(self, db: AsyncSession, external_id: str) -> Repository | None:
        """
        Fetch a connected repository by its external provider identifier (e.g. GitHub Repository ID).
        """
        query = select(Repository).filter(Repository.external_id == external_id)
        result = await db.execute(query)
        return result.scalars().first()

class RepositorySettingsRepository(BaseRepository[RepositorySettings, Any, Any]):
    def __init__(self):
        super().__init__(RepositorySettings)

    async def get_by_repository_id(self, db: AsyncSession, repository_id: uuid.UUID) -> RepositorySettings | None:
        """
        Fetch RepositorySettings by repository UUID.
        """
        query = select(RepositorySettings).filter(RepositorySettings.repository_id == repository_id)
        result = await db.execute(query)
        return result.scalars().first()

repository_repository = RepositoryRepository()
repository_settings_repository = RepositorySettingsRepository()
