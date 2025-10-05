from fastapi import Header, HTTPException, status, Depends, Cookie, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.services.snowflake_user_service import bump_usage_stats
from app.db.mongodb import get_database
from app.utils.security import verify_api_key as verify_api_key_hash
from app.services.jwt_service import verify_token
from app.services.auth_service import AuthService
from bson import ObjectId

security = HTTPBearer(auto_error=False)


async def get_auth_service(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token: Optional[str] = Cookie(None)
) -> AuthService:
    """
    Get authenticated AuthService instance.
    This is the main dependency to use for authentication.

    Returns an AuthService instance with the authenticated user loaded.
    Use auth_service.get_user_id(), auth_service.get_user(), etc.
    """
    auth_service = AuthService()

    token = credentials.credentials if credentials else None
    await auth_service.authenticate(token=token, cookie_token=access_token)

    return auth_service


# Legacy compatibility functions (deprecated, use get_auth_service instead)
async def verify_api_key(authorization: str = Header(...)):
    """
    API key authentication for MCP service
    DEPRECATED: Use get_auth_service instead
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    plain_api_key = authorization.replace("Bearer ", "")

    db = get_database()
    users = await db.users.find({}).to_list(length=None)

    for user in users:
        if "hashed_api_key" in user and verify_api_key_hash(plain_api_key, user["hashed_api_key"]):
            email = user.get("email")
            if email:
                await bump_usage_stats(email)
            return str(user["_id"])

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key"
    )


async def verify_jwt_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token: Optional[str] = Cookie(None)
):
    """
    JWT authentication for API endpoints
    DEPRECATED: Use get_auth_service instead
    """
    token = None

    if access_token:
        token = access_token
    elif credentials:
        token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - no token found in cookie or header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = verify_token(token, token_type="access")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    email = user.get("email")
    if email:
        await bump_usage_stats(email)

    return user_id


async def verify_refresh_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    refresh_token: Optional[str] = Cookie(None)
):
    """
    Verify refresh token for token refresh endpoint
    """
    token = None

    if refresh_token:
        token = refresh_token
    elif credentials:
        token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - no refresh token found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = verify_token(token, token_type="refresh")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    email = user.get("email")
    if email:
        await bump_usage_stats(email)

    return user_id


async def verify_jwt_or_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token: Optional[str] = Cookie(None)
):
    """
    Unified authentication: accepts both JWT (cookie/header) and API key
    DEPRECATED: Use get_auth_service instead
    """
    token = None

    if access_token:
        token = access_token
        user_id = verify_token(token, token_type="access")
        if user_id:
            db = get_database()
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                email = user.get("email")
                if email:
                    await bump_usage_stats(email)
                return user_id

    if credentials:
        token = credentials.credentials

        user_id = verify_token(token, token_type="access")
        if user_id:
            db = get_database()
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                email = user.get("email")
                if email:
                    await bump_usage_stats(email)
                return user_id

        db = get_database()
        users = await db.users.find({}).to_list(length=None)
        for user in users:
            if "hashed_api_key" in user and verify_api_key_hash(token, user["hashed_api_key"]):
                email = user.get("email")
                if email:
                    await bump_usage_stats(email)
                return str(user["_id"])

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated - provide valid JWT token or API key",
        headers={"WWW-Authenticate": "Bearer"},
    )
