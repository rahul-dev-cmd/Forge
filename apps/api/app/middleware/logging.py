import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        # Resolve request pipeline
        try:
            response = await call_next(request)
            duration = time.perf_counter() - start_time
            
            logger.info(
                f"HTTP {request.method} {request.url.path} completed in {duration:.4f}s with status {response.status_code}"
            )
            return response
        except Exception as e:
            duration = time.perf_counter() - start_time
            logger.exception(
                f"HTTP {request.method} {request.url.path} failed after {duration:.4f}s with error: {str(e)}"
            )
            raise e
