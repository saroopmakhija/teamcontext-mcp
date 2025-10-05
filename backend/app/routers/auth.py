from fastapi import APIRouter, HTTPException, status, Depends, Response
from app.models.user import UserCreate, UserResponse, UserLogin, TokenResponse
from app.db.mongodb import get_database
from app.utils.security import hash_password, verify_password, generate_api_key, hash_api_key
from app.dependencies import verify_jwt_or_api_key, verify_refresh_token
from app.services.jwt_service import create_access_token, create_refresh_token, ACCESS_TOKEN_EXPIRE_HOURS, REFRESH_TOKEN_EXPIRE_HOURS
from app.services.snowflake_user_service import create_user_record
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    """Register a new user and generate API key"""
    db = get_database()

    # Check if user already exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Generate API key and hash it
    plain_api_key = generate_api_key()

    # Create user document
    user_doc = {
        "email": user.email,
        "name": user.name,
        "hashed_password": hash_password(user.password),
        "hashed_api_key": hash_api_key(plain_api_key),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "is_active": True
    }

    result = await db.users.insert_one(user_doc)

    await create_user_record(user.email)

    # Return the plaintext API key only once - user must save it
    return UserResponse(
        id=str(result.inserted_id),
        email=user_doc["email"],
        name=user_doc["name"],
        api_key=plain_api_key,
        created_at=user_doc["created_at"]
    )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, response: Response):
    """Login with email/password and get JWT tokens (set in cookies)"""
    db = get_database()

    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    user_id = str(user["_id"])

    # Create JWT tokens
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    # Set cookies with secure flags
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_HOURS * 3600,  # Convert hours to seconds
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_HOURS * 3600,  # Convert hours to seconds
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(response: Response, user_id: str = Depends(verify_refresh_token)):
    """Refresh access token using refresh token (set in cookies)"""
    # Create new tokens
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    # Set cookies with secure flags
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        samesite="lax",
        secure=False
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_HOURS * 3600,
        samesite="lax",
        secure=False
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/logout")
async def logout(response: Response):
    """Logout by clearing JWT cookies"""
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"status": "success", "message": "Logged out successfully"}

@router.post("/api-key/rotate", response_model=UserResponse)
async def rotate_api_key(user_id: str = Depends(verify_jwt_or_api_key)):
    """Rotate API key for current user (requires JWT or API key auth)"""
    db = get_database()

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Generate new API key and hash it
    new_plain_api_key = generate_api_key()

    await db.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "hashed_api_key": hash_api_key(new_plain_api_key),
                "updated_at": datetime.utcnow()
            }
        }
    )

    # Return the plaintext API key only once - user must save it
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        name=user["name"],
        api_key=new_plain_api_key,
        created_at=user["created_at"]
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: str = Depends(verify_jwt_or_api_key)):
    """Get current user information (requires JWT or API key auth)"""
    db = get_database()

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        name=user["name"],
        api_key="***HIDDEN*** (API key only shown once at registration/rotation)",
        created_at=user["created_at"]
    )
