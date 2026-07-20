import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.organization import Organization, OrganizationMembership
from app.models.invitation import OrganizationInvitation
from app.models.enums import OrganizationRole, InvitationStatus
from app.services.user import user_service, UserCreate

pytestmark = pytest.mark.asyncio


async def _create_user(db: AsyncSession, username: str):
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


async def _seed_org(db: AsyncSession, owner_id, slug: str = "acme"):
    org = Organization(name="Acme Org", slug=slug, owner_id=owner_id)
    db.add(org)
    await db.commit()
    await db.refresh(org)
    membership = OrganizationMembership(
        organization_id=org.id,
        user_id=owner_id,
        role=OrganizationRole.OWNER.value,
    )
    db.add(membership)
    await db.commit()
    return org


async def test_invitation_create_accept_flow(client: AsyncClient, db: AsyncSession):
    owner = await _create_user(db, "johndoe")
    invitee = await _create_user(db, "invitee")
    org = await _seed_org(db, owner.id)

    headers = {"Authorization": "Bearer mock-token-johndoe"}
    create_res = await client.post(
        f"/api/v1/invitations/organizations/{org.id}/invitations",
        json={"email": invitee.email, "role": OrganizationRole.MEMBER.value},
        headers=headers,
    )
    assert create_res.status_code == 201
    token = create_res.json()["data"]["token"]

    # Duplicate pending invite rejected
    dup = await client.post(
        f"/api/v1/invitations/organizations/{org.id}/invitations",
        json={"email": invitee.email, "role": OrganizationRole.MEMBER.value},
        headers=headers,
    )
    assert dup.status_code == 400

    accept_res = await client.post(
        "/api/v1/invitations/accept",
        json={"token": token},
        headers={"Authorization": "Bearer mock-token-invitee"},
    )
    assert accept_res.status_code == 200
    assert accept_res.json()["data"]["role"] == OrganizationRole.MEMBER.value


async def test_invitation_expired(client: AsyncClient, db: AsyncSession):
    owner = await _create_user(db, "johndoe")
    invitee = await _create_user(db, "invitee")
    org = await _seed_org(db, owner.id, slug="expired-org")

    inv = OrganizationInvitation(
        organization_id=org.id,
        email=invitee.email,
        role=OrganizationRole.MEMBER.value,
        invited_by=owner.id,
        status=InvitationStatus.PENDING.value,
        token="expired-token-xyz",
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    db.add(inv)
    await db.commit()

    res = await client.post(
        "/api/v1/invitations/accept",
        json={"token": "expired-token-xyz"},
        headers={"Authorization": "Bearer mock-token-invitee"},
    )
    assert res.status_code == 400
    assert "expired" in res.json()["detail"].lower()


async def test_invitation_email_mismatch(client: AsyncClient, db: AsyncSession):
    owner = await _create_user(db, "johndoe")
    await _create_user(db, "invitee")
    await _create_user(db, "otheruser")
    org = await _seed_org(db, owner.id, slug="mismatch-org")

    headers = {"Authorization": "Bearer mock-token-johndoe"}
    create_res = await client.post(
        f"/api/v1/invitations/organizations/{org.id}/invitations",
        json={"email": "invitee@forge.com", "role": OrganizationRole.MEMBER.value},
        headers=headers,
    )
    token = create_res.json()["data"]["token"]

    res = await client.post(
        "/api/v1/invitations/accept",
        json={"token": token},
        headers={"Authorization": "Bearer mock-token-otheruser"},
    )
    assert res.status_code == 403


async def test_invitation_reject(client: AsyncClient, db: AsyncSession):
    owner = await _create_user(db, "johndoe")
    invitee = await _create_user(db, "invitee")
    org = await _seed_org(db, owner.id, slug="reject-org")

    headers = {"Authorization": "Bearer mock-token-johndoe"}
    create_res = await client.post(
        f"/api/v1/invitations/organizations/{org.id}/invitations",
        json={"email": invitee.email, "role": OrganizationRole.GUEST.value},
        headers=headers,
    )
    token = create_res.json()["data"]["token"]

    res = await client.post(
        "/api/v1/invitations/reject",
        json={"token": token},
        headers={"Authorization": "Bearer mock-token-invitee"},
    )
    assert res.status_code == 200


async def test_admin_cannot_invite_owner_or_admin(client: AsyncClient, db: AsyncSession):
    owner = await _create_user(db, "johndoe")
    admin = await _create_user(db, "adminuser")
    org = await _seed_org(db, owner.id, slug="hierarchy-org")

    db.add(
        OrganizationMembership(
            organization_id=org.id,
            user_id=admin.id,
            role=OrganizationRole.ADMIN.value,
        )
    )
    await db.commit()

    headers = {"Authorization": "Bearer mock-token-adminuser"}
    res = await client.post(
        f"/api/v1/invitations/organizations/{org.id}/invitations",
        json={"email": "newbie@forge.com", "role": OrganizationRole.ADMIN.value},
        headers=headers,
    )
    assert res.status_code == 403
    assert "equal to or higher" in res.json()["detail"]
