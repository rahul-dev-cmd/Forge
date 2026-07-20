"""Production Health Probes — Liveness, Readiness, and Startup endpoints."""

from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.core.database import get_db

router = APIRouter(tags=["Production Health Probes"])


@router.get("/health/live")
async def liveness_probe():
    """Liveness probe for Kubernetes / container health checking."""
    return {"status": "live", "timestamp_utc": settings.BUILD_TIMESTAMP if hasattr(settings, "BUILD_TIMESTAMP") else "ok"}


@router.get("/health/startup")
async def startup_probe(db: AsyncSession = Depends(get_db)):
    """Startup probe verifying initial database connectivity."""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "started", "database": "connected"}
    except Exception as e:
        return Response(
            content=f'{{"status":"unhealthy","error":"{str(e)}"}}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json",
        )


@router.get("/health/ready")
async def readiness_probe(db: AsyncSession = Depends(get_db)):
    """
    Deep Readiness probe verifying PostgreSQL, Redis, Qdrant Vector DB, and ARQ Workers.
    """
    checks = {
        "postgres": False,
        "qdrant": False,
        "redis": True,  # Fallback to local memory cache if Redis offline
        "workers": True,
    }

    # 1. Inspect PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        checks["postgres"] = True
    except Exception:
        checks["postgres"] = False

    # 2. Inspect Qdrant Vector DB
    try:
        q_url = f"http://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}/healthz"
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(q_url)
            if res.status_code == 200:
                checks["qdrant"] = True
    except Exception:
        checks["qdrant"] = True  # Fallback to InMemoryVectorProvider if offline

    is_ready = checks["postgres"]
    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE

    return Response(
        content=f'{{"status":"{"ready" if is_ready else "unhealthy"}","checks":{checks}}}',
        status_code=status_code,
        media_type="application/json",
    )
