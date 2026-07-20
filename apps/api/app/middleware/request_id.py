import uuid
import contextvars
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Global ContextVar to capture and share request ID across execution contexts (e.g., logging)
request_id_var = contextvars.ContextVar("request_id", default="")

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Fetch request ID if sent by client/gateway, or generate a fresh one
        req_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        
        # Bind request ID to the current async context
        token = request_id_var.set(req_id)
        request.state.request_id = req_id
        
        try:
            response = await call_next(request)
            response.headers["x-request-id"] = req_id
            return response
        finally:
            # Clean up token context on request wrap
            request_id_var.reset(token)
