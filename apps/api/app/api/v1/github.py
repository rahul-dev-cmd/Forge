"""GitHub App connect / install / installation listing APIs."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.github_service import (
    github_service,
    GitHubConnectRequest,
    GitHubInstallRequest,
)
from app.utils.response import wrap_response

router = APIRouter()


@router.post("/connect")
async def github_connect(
    body: GitHubConnectRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Start GitHub OAuth account linking (GitHub App user-to-server).
    Returns authorize_url — never returns tokens.
    """
    data = github_service.start_connect(user_id=current_user.id, body=body)
    return wrap_response(data=data, message="GitHub connect URL generated.")


@router.post("/install")
async def github_install(
    body: GitHubInstallRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Start GitHub App installation, or register an installation_id after redirect.
    """
    if body.installation_id:
        inst = await github_service.register_installation(
            db,
            user_id=current_user.id,
            installation_id=body.installation_id,
            workspace_id=body.workspace_id,
        )
        return wrap_response(
            data={
                "installation": {
                    "id": str(inst.id),
                    "installation_id": inst.installation_id,
                    "account_login": inst.account_login,
                    "status": inst.status,
                }
            },
            message="GitHub App installation registered.",
        )

    data = github_service.start_install(body=body)
    return wrap_response(data=data, message="GitHub App install URL generated.")


@router.get("/callback")
async def github_oauth_callback_redirect(
    code: str | None = None,
    installation_id: str | None = None,
    setup_action: str | None = None,
    state: str | None = None,
):
    """
    Browser redirect from GitHub. Forwards params to the frontend (no tokens exposed).
    Authenticated completion happens via POST /github/complete.
    """
    frontend = settings.FRONTEND_URL.rstrip("/")
    params = []
    if code:
        params.append(f"code={code}")
    if installation_id:
        params.append(f"installation_id={installation_id}")
    if setup_action:
        params.append(f"setup_action={setup_action}")
    if state:
        params.append(f"state={state}")
    qs = ("&".join(params)) if params else ""
    return RedirectResponse(url=f"{frontend}/repositories?github=callback&{qs}")


@router.post("/complete")
async def github_complete(
    code: str | None = Query(None),
    installation_id: str | None = Query(None),
    workspace_id: uuid.UUID | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Complete OAuth linking or App installation registration (authenticated)."""
    if installation_id:
        inst = await github_service.register_installation(
            db,
            user_id=current_user.id,
            installation_id=installation_id,
            workspace_id=workspace_id,
        )
        return wrap_response(
            data={
                "mode": "install",
                "installation": {
                    "id": str(inst.id),
                    "installation_id": inst.installation_id,
                    "account_login": inst.account_login,
                    "status": inst.status,
                },
            },
            message="GitHub App installation registered.",
        )
    if code:
        result = await github_service.complete_oauth_callback(
            db, user_id=current_user.id, code=code, workspace_id=workspace_id
        )
        return wrap_response(data={"mode": "oauth", **result}, message="GitHub account linked.")
    raise HTTPException(status_code=400, detail="Provide code or installation_id")


@router.get("/installations")
async def list_installations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await github_service.list_installations(db, user_id=current_user.id)
    return wrap_response(data=items)


@router.get("/repositories")
async def list_github_repositories(
    installation_id: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List repositories available via the user's GitHub App installations.
    """
    data = await github_service.list_available_repositories(
        db,
        user_id=current_user.id,
        installation_id=installation_id,
        page=page,
        per_page=per_page,
    )
    return wrap_response(
        data=data.get("items", []),
        page=data.get("page", page),
        limit=per_page,
        total=data.get("total_count", 0),
        message=data.get("message") or "",
    )
