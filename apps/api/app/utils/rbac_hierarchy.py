"""
Role hierarchy helpers for workspace and organization membership updates.

Workspace: Owner > Admin > Manager > Developer > Viewer
Organization: Owner > Admin > Member > Guest

An actor cannot assign a role higher than or equal to their own, and cannot
modify members whose current role is higher than or equal to the actor's.
"""

from fastapi import HTTPException, status
from app.models.enums import WorkspaceRole, OrganizationRole

WORKSPACE_ROLE_RANK: dict[str, int] = {
    WorkspaceRole.OWNER.value: 5,
    WorkspaceRole.ADMIN.value: 4,
    WorkspaceRole.MANAGER.value: 3,
    WorkspaceRole.DEVELOPER.value: 2,
    WorkspaceRole.VIEWER.value: 1,
}

ORGANIZATION_ROLE_RANK: dict[str, int] = {
    OrganizationRole.OWNER.value: 4,
    OrganizationRole.ADMIN.value: 3,
    OrganizationRole.MEMBER.value: 2,
    OrganizationRole.GUEST.value: 1,
}


def _rank(role: str, ranking: dict[str, int], label: str) -> int:
    value = ranking.get(role)
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {label} role: '{role}'.",
        )
    return value


def workspace_role_rank(role: str) -> int:
    return _rank(role, WORKSPACE_ROLE_RANK, "workspace")


def organization_role_rank(role: str) -> int:
    return _rank(role, ORGANIZATION_ROLE_RANK, "organization")


def assert_can_assign_workspace_role(actor_role: str, new_role: str) -> None:
    """Actor may only assign roles strictly below their own rank."""
    if workspace_role_rank(new_role) >= workspace_role_rank(actor_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot assign a role equal to or higher than your own.",
        )


def assert_can_manage_workspace_member(actor_role: str, target_role: str) -> None:
    """Actor may only manage members whose current role is strictly below theirs."""
    if workspace_role_rank(target_role) >= workspace_role_rank(actor_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify a member with equal or higher role.",
        )


def assert_can_assign_org_role(actor_role: str, new_role: str) -> None:
    """Actor may only assign org roles strictly below their own rank."""
    if organization_role_rank(new_role) >= organization_role_rank(actor_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot assign a role equal to or higher than your own.",
        )


def assert_can_manage_org_member(actor_role: str, target_role: str) -> None:
    """Actor may only manage org members whose current role is strictly below theirs."""
    if organization_role_rank(target_role) >= organization_role_rank(actor_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify a member with equal or higher role.",
        )
