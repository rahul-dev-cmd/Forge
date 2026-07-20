from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class WorkspaceMemberBase(BaseModel):
    user_id: UUID
    role: str

class WorkspaceMember(WorkspaceMemberBase):
    id: UUID
    workspace_id: UUID
    joined_at: datetime

    class Config:
        from_attributes = True

class WorkspaceBase(BaseModel):
    name: str
    slug: str
    description: str | None = None

class WorkspaceCreate(WorkspaceBase):
    owner_id: UUID
    organization_id: UUID | None = None

class WorkspaceUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None

class WorkspaceResponse(WorkspaceBase):
    id: UUID
    owner_id: UUID
    organization_id: UUID | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
