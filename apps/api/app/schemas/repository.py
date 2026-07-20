from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class RepositorySettingsBase(BaseModel):
    ai_enabled: bool
    indexing_enabled: bool
    auto_sync: bool
    sync_interval: int

class RepositorySettingsUpdate(BaseModel):
    ai_enabled: bool | None = None
    indexing_enabled: bool | None = None
    auto_sync: bool | None = None
    sync_interval: int | None = None

class RepositorySettings(RepositorySettingsBase):
    id: UUID
    repository_id: UUID

    class Config:
        from_attributes = True

class RepositoryBase(BaseModel):
    provider: str
    external_id: str
    name: str
    default_branch: str
    clone_url: str
    installation_id: str | None = None

class RepositoryCreate(RepositoryBase):
    project_id: UUID
    workspace_id: UUID

class RepositoryUpdate(BaseModel):
    name: str | None = None
    default_branch: str | None = None
    clone_url: str | None = None
    installation_id: str | None = None

class RepositoryResponse(RepositoryBase):
    id: UUID
    project_id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
