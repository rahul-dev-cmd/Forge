import time
from typing import Dict, List
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.settings import settings
from app.utils.logger import logger

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit: int = None):
        super().__init__(app)
        self.rate_limit = rate_limit or settings.RATE_LIMIT_PER_MINUTE
        # In-memory store: maps client IP strings to lists of timestamps
        self.ip_window: Dict[str, List[float]] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()

        # Retrieve request logs and slide window to include only last 60 seconds
        timestamps = self.ip_window.get(client_ip, [])
        timestamps = [t for t in timestamps if now - t < 60]

        if len(timestamps) >= self.rate_limit:
            logger.warning(f"Rate limit exceeded: {client_ip} triggered {len(timestamps)} requests/min")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Please wait before retrying."}
            )

        timestamps.append(now)
        self.ip_window[client_ip] = timestamps

        return await call_next(request)
