import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workspace import Workspace, WorkspaceMember
from app.models.project import Project
from app.models.enums import WorkspaceRole
from app.services.user import user_service, UserCreate

pytestmark = pytest.mark.asyncio

async def test_concurrency_optimistic_locking_conflict(client: AsyncClient, db: AsyncSession):
    """
    Assert that updating a project with a stale version throws a 409 Conflict error.
    """
    # 1. Sync the mock user 'johndoe' to obtain their ID
    user_in = UserCreate(
        email="johndoe@forge.com",
        username="johndoe",
        full_name="John Doe",
        avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=80&fit=crop",
        clerk_id="clerk-mock-johndoe"
    )
    user = await user_service.get_or_create_user(db, user_in)
    user_id = user.id

    # 2. Create the test workspace
    workspace = Workspace(
        name="Concurrency Workspace",
        slug="concurrency-ws",
        owner_id=user_id
    )
    db.add(workspace)
    await db.commit()
    await db.refresh(workspace)

    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=user_id,
        role=WorkspaceRole.OWNER.value
    )
    db.add(member)

    # 3. Create the project with initial version = 1
    project = Project(
        workspace_id=workspace.id,
        owner_id=user_id,
        name="Concurrency Test Project",
        slug="concurrency-test",
        version=1
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    # 4. Update with expected version = 1 (should succeed and increment version to 2)
    headers = {"Authorization": "Bearer mock-token-johndoe"}
    update_payload = {
        "name": "Updated Concurrency Project name",
        "version": 1
    }
    response = await client.patch(f"/api/v1/projects/{project.id}", json=update_payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["data"]["version"] == 2

    # 5. Attempt update with expected version = 1 again (stale version)
    stale_payload = {
        "name": "Stale Concurrent Modification",
        "version": 1
    }
    conflict_res = await client.patch(f"/api/v1/projects/{project.id}", json=stale_payload, headers=headers)
    
    assert conflict_res.status_code == 409
    assert "Conflict: Project has been modified" in conflict_res.json()["detail"]
