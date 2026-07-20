import jwt
import httpx
from typing import Optional, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.settings import settings
from app.core.database import get_db
from app.services.user import user_service, UserCreate
from app.utils.logger import logger

security = HTTPBearer()

# In-memory cache for Clerk public signature keys
jwks_cache: Optional[dict] = None

def is_clerk_configured() -> bool:
    """
    Check if backend is configured with actual Clerk signature keys.
    """
    return (
        settings.CLERK_SECRET_KEY is not None and 
        not settings.CLERK_SECRET_KEY.startswith("sk_test_placeholder")
    )

async def get_jwks() -> dict:
    global jwks_cache
    if jwks_cache:
        return jwks_cache

    try:
        async with httpx.AsyncClient() as client:
            headers = {}
            if is_clerk_configured():
                headers["Authorization"] = f"Bearer {settings.CLERK_SECRET_KEY}"
            
            response = await client.get(settings.CLERK_JWKS_URL, headers=headers)
            response.raise_for_status()
            jwks_cache = response.json()
            return jwks_cache
    except Exception as e:
        logger.exception("Failed to fetch signature keys from Clerk JWKS endpoint")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication configurations validation error on server."
        )

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header credentials missing."
        )

    token = credentials.credentials

    # Mock Auth Fallback Path (if Clerk keys are placeholders or mock token is received)
    if not is_clerk_configured() or token.startswith("mock-token-"):
        # Resolve username parameters from token slug
        mock_username = "rahuldev"
        if token.startswith("mock-token-"):
            mock_username = token.replace("mock-token-", "")

        user_in = UserCreate(
            email=f"{mock_username}@forge.com",
            username=mock_username,
            full_name=mock_username.title().replace("dev", " Dev"),
            avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=80&fit=crop",
            clerk_id=f"clerk-mock-{mock_username}"
        )
        user = await user_service.get_or_create_user(db, user_in)
        return user

    # Live Clerk JWKS Verification Path
    jwks = await get_jwks()

    try:
        unverified_header = jwt.get_unverified_header(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed authentication header token format."
        )

    kid = unverified_header.get("kid")
    if not kid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header key identifier (kid) missing in session token."
        )

    # Resolve matching signature keys
    public_key = None
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            # Map key properties from JWK standard format
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
            break

    if not public_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signature key verification identifier not found."
        )

    try:
        # Decode and verify RS256 token signatures
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={"verify_aud": False} # Clerk tokens might map aud to client dashboard URL
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token has expired. Please log in again."
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Verification check failed: {str(e)}"
        )

    clerk_id = payload.get("sub")
    if not clerk_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing subject clerk id identifier."
        )

    # Extract user profile information
    email = payload.get("email") or payload.get("primary_email_address")
    if not email:
        email = f"{clerk_id}@clerk.accounts.dev"

    full_name = payload.get("name") or payload.get("full_name") or "User"
    username = payload.get("username")

    user_in = UserCreate(
        email=email,
        username=username,
        full_name=full_name,
        avatar_url=payload.get("picture"),
        clerk_id=clerk_id
    )

    user = await user_service.get_or_create_user(db, user_in)
    return user
