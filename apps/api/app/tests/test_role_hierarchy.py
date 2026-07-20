import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workspace import Workspace, WorkspaceMember
from app.models.enums import WorkspaceRole
from app.services.user import user_service, UserCreate

pytestmark = pytest.mark.asyncio


async def _user(db: AsyncSession, username: str):
    return await user_service.get_or_create_user(
        db,
        UserCreate(
            email=f"{username}@forge.com",
            username=username,
            full_name=username.title(),
            avatar_url="https://example.com/a.png",
            clerk_id=f"clerk-mock-{username}",
        ),
    )


async def _workspace_with_roles(db: AsyncSession):
    owner = await _user(db, "wsowner")
    admin = await _user(db, "wsadmin")
    developer = await _user(db, "wsdev")

    workspace = Workspace(name="Hierarchy WS", slug="hierarchy-ws", owner_id=owner.id)
    db.add(workspace)
    await db.commit()
    await db.refresh(workspace)

    for user, role in [
        (owner, WorkspaceRole.OWNER.value),
        (admin, WorkspaceRole.ADMIN.value),
        (developer, WorkspaceRole.DEVELOPER.value),
    ]:
        db.add(
            WorkspaceMember(
                workspace_id=workspace.id,
                user_id=user.id,
                role=role,
            )
        )
    await db.commit()
    return workspace, owner, admin, developer


async def test_admin_cannot_promote_to_owner(client: AsyncClient, db: AsyncSession):
    workspace, _, admin, developer = await _workspace_with_roles(db)

    res = await client.patch(
        f"/api/v1/workspaces/{workspace.id}/members/{developer.id}",
        params={"role": WorkspaceRole.OWNER.value},
        headers={"Authorization": "Bearer mock-token-wsadmin"},
    )
    assert res.status_code == 403


async def test_admin_cannot_assign_admin(client: AsyncClient, db: AsyncSession):
    workspace, _, _, developer = await _workspace_with_roles(db)

    res = await client.patch(
        f"/api/v1/workspaces/{workspace.id}/members/{developer.id}",
        params={"role": WorkspaceRole.ADMIN.value},
        headers={"Authorization": "Bearer mock-token-wsadmin"},
    )
    assert res.status_code == 403
    assert "equal to or higher" in res.json()["detail"]


async def test_admin_can_promote_to_manager(client: AsyncClient, db: AsyncSession):
    workspace, _, _, developer = await _workspace_with_roles(db)

    res = await client.patch(
        f"/api/v1/workspaces/{workspace.id}/members/{developer.id}",
        params={"role": WorkspaceRole.MANAGER.value},
        headers={"Authorization": "Bearer mock-token-wsadmin"},
    )
    assert res.status_code == 200
    assert res.json()["data"]["role"] == WorkspaceRole.MANAGER.value


async def test_admin_cannot_demote_owner(client: AsyncClient, db: AsyncSession):
    workspace, owner, _, _ = await _workspace_with_roles(db)

    res = await client.patch(
        f"/api/v1/workspaces/{workspace.id}/members/{owner.id}",
        params={"role": WorkspaceRole.DEVELOPER.value},
        headers={"Authorization": "Bearer mock-token-wsadmin"},
    )
    assert res.status_code == 403
    assert "equal or higher" in res.json()["detail"]


async def test_admin_cannot_remove_owner(client: AsyncClient, db: AsyncSession):
    workspace, owner, _, _ = await _workspace_with_roles(db)

    res = await client.delete(
        f"/api/v1/workspaces/{workspace.id}/members/{owner.id}",
        headers={"Authorization": "Bearer mock-token-wsadmin"},
    )
    assert res.status_code == 403
