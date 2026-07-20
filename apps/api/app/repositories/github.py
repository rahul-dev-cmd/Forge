from typing import Any, List
import uuid
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.github import GitHubInstallation, GitHubAccountLink
from app.repositories.base import BaseRepository


class GitHubInstallationRepository(BaseRepository[GitHubInstallation, Any, Any]):
    def __init__(self):
        super().__init__(GitHubInstallation)

    async def get_by_installation_id(
        self, db: AsyncSession, installation_id: str
    ) -> GitHubInstallation | None:
        result = await db.execute(
            select(GitHubInstallation).filter(
                GitHubInstallation.installation_id == installation_id
            )
        )
        return result.scalars().first()

    async def list_for_user(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> List[GitHubInstallation]:
        result = await db.execute(
            select(GitHubInstallation)
            .filter(GitHubInstallation.user_id == user_id)
            .order_by(GitHubInstallation.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_for_workspace(
        self, db: AsyncSession, workspace_id: uuid.UUID
    ) -> List[GitHubInstallation]:
        result = await db.execute(
            select(GitHubInstallation).filter(
                GitHubInstallation.workspace_id == workspace_id
            )
        )
        return list(result.scalars().all())


class GitHubAccountLinkRepository(BaseRepository[GitHubAccountLink, Any, Any]):
    def __init__(self):
        super().__init__(GitHubAccountLink)

    async def get_by_user(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> GitHubAccountLink | None:
        result = await db.execute(
            select(GitHubAccountLink).filter(GitHubAccountLink.user_id == user_id)
        )
        return result.scalars().first()


github_installation_repository = GitHubInstallationRepository()
github_account_link_repository = GitHubAccountLinkRepository()
