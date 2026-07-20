import asyncio
import urllib.parse
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.config.settings import settings

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Perform deep health check checking API, PostgreSQL connection, DB version, and Redis.
    """
    health_status = {
        "api_status": "ok",
        "postgres_status": "disconnected",
        "postgres_version": None,
        "redis_status": "disconnected"
    }

    # 1. Verify PostgreSQL Database connection and query engine version
    try:
        result = await db.execute(text("SHOW server_version"))
        version = result.scalar()
        health_status["postgres_status"] = "connected"
        health_status["postgres_version"] = version
    except Exception:
        # Connection failed or query error
        health_status["postgres_status"] = "disconnected"

    # 2. Verify Redis server state using lightweight standard library socket ping
    try:
        parsed_url = urllib.parse.urlparse(settings.REDIS_URL)
        host = parsed_url.hostname or "localhost"
        port = parsed_url.port or 6379
        
        # Async socket connection check
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=1.0
        )
        writer.close()
        await writer.wait_closed()
        health_status["redis_status"] = "connected"
    except Exception:
        # Port inactive or connection timed out
        health_status["redis_status"] = "disconnected"

    return health_status
