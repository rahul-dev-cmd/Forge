from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ProjectSettingsBase(BaseModel):
    default_branch: str
    coding_style: str
    preferred_language: str
    ai_enabled: bool

class ProjectSettingsUpdate(BaseModel):
    default_branch: str | None = None
    coding_style: str | None = None
    preferred_language: str | None = None
    ai_enabled: bool | None = None

class ProjectSettings(ProjectSettingsBase):
    id: UUID
    project_id: UUID

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str
    slug: str
    description: str | None = None

class ProjectCreate(ProjectBase):
    workspace_id: UUID
    owner_id: UUID

class ProjectUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None

class ProjectResponse(ProjectBase):
    id: UUID
    workspace_id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
