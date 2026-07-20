import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.repository import Repository, RepositorySettings
from app.models.audit_log import AuditLog
from app.repositories.repository import repository_repository, repository_settings_repository
from pydantic import BaseModel

class RepositoryCreate(BaseModel):
    project_id: uuid.UUID
    workspace_id: uuid.UUID
    provider: str
    external_id: str
    name: str
    default_branch: str
    clone_url: str
    installation_id: str | None = None

class RepositoryUpdate(BaseModel):
    name: str | None = None
    default_branch: str | None = None
    clone_url: str | None = None
    installation_id: str | None = None

class RepositorySettingsUpdate(BaseModel):
    ai_enabled: bool | None = None
    indexing_enabled: bool | None = None
    auto_sync: bool | None = None
    sync_interval: int | None = None

class RepositoryService:
    async def create_repository(self, db: AsyncSession, repo_in: RepositoryCreate, actor_id: uuid.UUID, ip_address: str | None = None) -> Repository:
        """
        Create a Repository record, initialize default settings, and write an audit log.
        """
        # Create Repository
        repo = await repository_repository.create(db, obj_in=repo_in)

        # Create RepositorySettings
        settings_obj = RepositorySettings(
            repository_id=repo.id,
            ai_enabled=True,
            indexing_enabled=True,
            auto_sync=True,
            sync_interval=3600
        )
        db.add(settings_obj)
        await db.commit()
        await db.refresh(repo)

        # Audit log creation
        log = AuditLog(
            actor_id=actor_id,
            action="repository_creation",
            target_type="repository",
            target_id=repo.id,
            details={"name": repo.name, "provider": repo.provider, "external_id": repo.external_id},
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()

        return repo

    async def get_repository(self, db: AsyncSession, repo_id: uuid.UUID) -> Repository | None:
        """
        Fetch a repository by UUID.
        """
        return await repository_repository.get(db, repo_id)

    async def get_by_project(self, db: AsyncSession, project_id: uuid.UUID) -> List[Repository]:
        """
        Get all repositories inside a project.
        """
        return await repository_repository.get_by_project(db, project_id)

    async def update_settings(self, db: AsyncSession, repo_id: uuid.UUID, settings_in: RepositorySettingsUpdate, actor_id: uuid.UUID, ip_address: str | None = None) -> RepositorySettings | None:
        """
        Update repository settings and audit log the changes.
        """
        settings = await repository_settings_repository.get_by_repository_id(db, repo_id)
        if not settings:
            return None
        
        updated = await repository_settings_repository.update(db, db_obj=settings, obj_in=settings_in)

        # Audit log settings update
        log = AuditLog(
            actor_id=actor_id,
            action="settings_change",
            target_type="repository_settings",
            target_id=repo_id,
            details=settings_in.model_dump(exclude_unset=True),
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()

        return updated

repository_service = RepositoryService()
