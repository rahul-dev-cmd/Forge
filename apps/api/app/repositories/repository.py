from typing import Any, List
import uuid
from sqlalchemy import select, or_, func, and_
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
        query = select(Repository).filter(
            Repository.project_id == project_id,
            Repository.deleted_at.is_(None),
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_external_id(self, db: AsyncSession, external_id: str) -> Repository | None:
        """
        Fetch a connected repository by its external provider identifier (e.g. GitHub Repository ID).
        """
        query = select(Repository).filter(
            Repository.external_id == external_id,
            Repository.deleted_at.is_(None),
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_provider_repository_id(
        self, db: AsyncSession, provider_repository_id: str
    ) -> Repository | None:
        result = await db.execute(
            select(Repository).filter(
                or_(
                    Repository.provider_repository_id == provider_repository_id,
                    Repository.external_id == provider_repository_id,
                ),
                Repository.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    async def list_for_workspace(
        self,
        db: AsyncSession,
        workspace_id: uuid.UUID,
        *,
        query: str | None = None,
        sync_status: str | None = None,
        sort_by: str = "updated_at",
        order: str = "desc",
        page: int = 1,
        limit: int = 20,
    ) -> tuple[List[Repository], int]:
        filters = [
            Repository.workspace_id == workspace_id,
            Repository.deleted_at.is_(None),
        ]
        if query:
            like = f"%{query}%"
            filters.append(
                or_(
                    Repository.name.ilike(like),
                    Repository.full_name.ilike(like),
                    Repository.owner.ilike(like),
                )
            )
        if sync_status:
            filters.append(Repository.sync_status == sync_status)

        count_q = select(func.count()).select_from(Repository).where(and_(*filters))
        total = (await db.execute(count_q)).scalar() or 0

        sort_col = getattr(Repository, sort_by, Repository.updated_at)
        ordering = sort_col.desc() if order == "desc" else sort_col.asc()
        result = await db.execute(
            select(Repository)
            .where(and_(*filters))
            .order_by(ordering)
            .offset((page - 1) * limit)
            .limit(limit)
        )
        return list(result.scalars().all()), int(total)

    async def list_auto_sync_due(
        self, db: AsyncSession, *, limit: int = 50
    ) -> List[Repository]:
        result = await db.execute(
            select(Repository)
            .join(RepositorySettings)
            .filter(
                Repository.deleted_at.is_(None),
                RepositorySettings.auto_sync.is_(True),
                Repository.connection_status == "connected",
            )
            .limit(limit)
        )
        return list(result.scalars().all())

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
