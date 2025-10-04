from fastapi import Header, HTTPException, status
from app.db.mongodb import get_database
from app.utils.security import verify_api_key as verify_api_key_hash

async def verify_api_key(authorization: str = Header(...)):
    """
    API key authentication by checking hashed API key in database
    Format: Authorization: Bearer <api_key>
    Returns: user_id (str) of authenticated user
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    plain_api_key = authorization.replace("Bearer ", "")

    # Get all users and verify API key hash
    # Note: This is not efficient - should add indexing and better querying
    db = get_database()

    # For security, we need to check hash against all users
    # A better approach would be to include a user identifier in the API key
    users = await db.users.find({}).to_list(length=None)

    for user in users:
        if "hashed_api_key" in user and verify_api_key_hash(plain_api_key, user["hashed_api_key"]):
            # Return user_id for downstream use
            return str(user["_id"])

    # No matching API key found
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key"
    )
