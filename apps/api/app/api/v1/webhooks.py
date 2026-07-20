"""GitHub webhook receiver — signature verified, logged, queued."""

from fastapi import APIRouter, Depends, Header, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.webhook_service import webhook_service
from app.utils.response import wrap_response
from app.utils.logger import logger

router = APIRouter()


@router.post("/github")
async def receive_github_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_hub_signature_256: str | None = Header(None, alias="X-Hub-Signature-256"),
    x_github_delivery: str | None = Header(None, alias="X-GitHub-Delivery"),
    x_github_event: str | None = Header(None, alias="X-GitHub-Event"),
):
    if not x_github_delivery or not x_github_event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-GitHub-Delivery or X-GitHub-Event headers",
        )

    body = await request.body()
    result = await webhook_service.ingest(
        db,
        delivery_id=x_github_delivery,
        event_type=x_github_event,
        signature_header=x_hub_signature_256,
        payload_body=body,
    )

    if not result.get("accepted"):
        logger.warning("Webhook rejected", extra=result)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )

    return wrap_response(data=result, message="Webhook accepted.")
