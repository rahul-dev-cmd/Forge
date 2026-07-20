from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.api.v1.router import api_router
from app.middleware.request_id import RequestIdMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

# Customized OpenAPI Forge branding documentation
app = FastAPI(
    title="Forge Backend API Engine",
    version="1.0.0",
    description="Scalable, repository-aware developer assistant backend. Interfaces databases, repositories sync, and Clerk authentication services.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 1. Inject unique request IDs into request scope (must execute first)
app.add_middleware(RequestIdMiddleware)

# 2. Structured JSON uvicorn requests/errors logging
app.add_middleware(LoggingMiddleware)

# 3. sliding window rate limiter
app.add_middleware(RateLimitMiddleware)

# 4. restricted CORS parameters
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API endpoints
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")
