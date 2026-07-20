from typing import Any, List
import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.git_metadata import (
    Branch,
    Commit,
    PullRequest,
    Issue,
    Contributor,
    RepositoryLanguage,
    RepositoryTopic,
)
from app.repositories.base import BaseRepository


class BranchRepository(BaseRepository[Branch, Any, Any]):
    def __init__(self):
        super().__init__(Branch)

    async def list_for_repository(
        self, db: AsyncSession, repository_id: uuid.UUID
    ) -> List[Branch]:
        result = await db.execute(
            select(Branch)
            .filter(Branch.repository_id == repository_id)
            .order_by(Branch.is_default.desc(), Branch.name.asc())
        )
        return list(result.scalars().all())

    async def get_by_name(
        self, db: AsyncSession, repository_id: uuid.UUID, name: str
    ) -> Branch | None:
        result = await db.execute(
            select(Branch).filter(
                Branch.repository_id == repository_id, Branch.name == name
            )
        )
        return result.scalars().first()


class CommitRepository(BaseRepository[Commit, Any, Any]):
    def __init__(self):
        super().__init__(Commit)

    async def list_for_repository(
        self, db: AsyncSession, repository_id: uuid.UUID, *, limit: int = 50
    ) -> List[Commit]:
        result = await db.execute(
            select(Commit)
            .filter(Commit.repository_id == repository_id)
            .order_by(Commit.committed_at.desc().nullslast())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_sha(
        self, db: AsyncSession, repository_id: uuid.UUID, sha: str
    ) -> Commit | None:
        result = await db.execute(
            select(Commit).filter(
                Commit.repository_id == repository_id, Commit.commit_sha == sha
            )
        )
        return result.scalars().first()


class PullRequestRepository(BaseRepository[PullRequest, Any, Any]):
    def __init__(self):
        super().__init__(PullRequest)

    async def list_for_repository(
        self, db: AsyncSession, repository_id: uuid.UUID, *, limit: int = 30
    ) -> List[PullRequest]:
        result = await db.execute(
            select(PullRequest)
            .filter(PullRequest.repository_id == repository_id)
            .order_by(PullRequest.provider_updated_at.desc().nullslast())
            .limit(limit)
        )
        return list(result.scalars().all())


class IssueRepository(BaseRepository[Issue, Any, Any]):
    def __init__(self):
        super().__init__(Issue)

    async def list_for_repository(
        self, db: AsyncSession, repository_id: uuid.UUID, *, limit: int = 30
    ) -> List[Issue]:
        result = await db.execute(
            select(Issue)
            .filter(Issue.repository_id == repository_id)
            .order_by(Issue.provider_updated_at.desc().nullslast())
            .limit(limit)
        )
        return list(result.scalars().all())


class ContributorRepository(BaseRepository[Contributor, Any, Any]):
    def __init__(self):
        super().__init__(Contributor)

    async def list_for_repository(
        self, db: AsyncSession, repository_id: uuid.UUID
    ) -> List[Contributor]:
        result = await db.execute(
            select(Contributor)
            .filter(Contributor.repository_id == repository_id)
            .order_by(Contributor.contributions.desc())
        )
        return list(result.scalars().all())


class LanguageRepository(BaseRepository[RepositoryLanguage, Any, Any]):
    def __init__(self):
        super().__init__(RepositoryLanguage)

    async def list_for_repository(
        self, db: AsyncSession, repository_id: uuid.UUID
    ) -> List[RepositoryLanguage]:
        result = await db.execute(
            select(RepositoryLanguage)
            .filter(RepositoryLanguage.repository_id == repository_id)
            .order_by(RepositoryLanguage.percentage.desc())
        )
        return list(result.scalars().all())

    async def replace_for_repository(
        self, db: AsyncSession, repository_id: uuid.UUID, languages: list[RepositoryLanguage]
    ) -> None:
        await db.execute(
            delete(RepositoryLanguage).where(
                RepositoryLanguage.repository_id == repository_id
            )
        )
        for lang in languages:
            db.add(lang)


class TopicRepository(BaseRepository[RepositoryTopic, Any, Any]):
    def __init__(self):
        super().__init__(RepositoryTopic)

    async def list_for_repository(
        self, db: AsyncSession, repository_id: uuid.UUID
    ) -> List[RepositoryTopic]:
        result = await db.execute(
            select(RepositoryTopic).filter(
                RepositoryTopic.repository_id == repository_id
            )
        )
        return list(result.scalars().all())

    async def replace_for_repository(
        self, db: AsyncSession, repository_id: uuid.UUID, topics: list[RepositoryTopic]
    ) -> None:
        await db.execute(
            delete(RepositoryTopic).where(RepositoryTopic.repository_id == repository_id)
        )
        for topic in topics:
            db.add(topic)


branch_repository = BranchRepository()
commit_repository = CommitRepository()
pull_request_repository = PullRequestRepository()
issue_repository = IssueRepository()
contributor_repository = ContributorRepository()
language_repository = LanguageRepository()
topic_repository = TopicRepository()
