import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workspace import Workspace, WorkspaceMember
from app.models.project import Project
from app.models.enums import WorkspaceRole
from app.services.user import user_service, UserCreate

pytestmark = pytest.mark.asyncio

async def test_rbac_insufficient_permissions(client: AsyncClient, db: AsyncSession):
    """
    Assert that a workspace Viewer cannot delete a project.
    """
    # 1. Sync the mock user 'johndoe' in the test database to obtain their ID
    user_in = UserCreate(
        email="johndoe@forge.com",
        username="johndoe",
        full_name="John Doe",
        avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=80&fit=crop",
        clerk_id="clerk-mock-johndoe"
    )
    user = await user_service.get_or_create_user(db, user_in)
    user_id = user.id

    # 2. Create the test workspace owned by another user (or johndoe)
    workspace = Workspace(
        name="Test Permissions Workspace",
        slug="test-perms-ws",
        owner_id=user_id
    )
    db.add(workspace)
    await db.commit()
    await db.refresh(workspace)

    # 3. Create a project in the workspace
    project = Project(
        workspace_id=workspace.id,
        owner_id=user_id,
        name="Test Perm Project",
        slug="test-perm-proj",
        version=1
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    # 4. Add johndoe as a Viewer in the workspace members list
    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=user_id,
        role=WorkspaceRole.VIEWER.value
    )
    db.add(member)
    await db.commit()

    # 5. Request deletion of the project using Viewer token
    headers = {"Authorization": "Bearer mock-token-johndoe"}
    
    response = await client.delete(f"/api/v1/projects/{project.id}", headers=headers)
    
    assert response.status_code == 403
    assert "Insufficient workspace permissions" in response.json()["detail"]
