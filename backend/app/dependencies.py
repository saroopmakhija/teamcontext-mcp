from fastapi import Header, HTTPException, status
from app.db.mongodb import get_database

async def verify_api_key(authorization: str = Header(...)):
    """
    API key authentication by checking against user's API key in database
    Format: Authorization: Bearer <api_key>
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    api_key = authorization.replace("Bearer ", "")

    # Check if API key exists in database
    db = get_database()
    user = await db.users.find_one({"api_key": api_key})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    return api_key
