from fastapi import APIRouter, HTTPException, status, Depends
from app.models.user import UserCreate, UserResponse, UserLogin
from app.db.mongodb import get_database
from app.utils.security import hash_password, verify_password, generate_api_key, hash_api_key
from app.dependencies import verify_api_key
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
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True
    }

    result = await db.users.insert_one(user_doc)

    # Return the plaintext API key only once - user must save it
    return UserResponse(
        id=str(result.inserted_id),
        email=user_doc["email"],
        name=user_doc["name"],
        api_key=plain_api_key,
        created_at=user_doc["created_at"]
    )

@router.post("/login", response_model=UserResponse)
async def login(credentials: UserLogin):
    """Login and get user info (API key cannot be retrieved after registration)"""
    db = get_database()

    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        name=user["name"],
        api_key="***HIDDEN*** (API key only shown once at registration/rotation)",
        created_at=user["created_at"]
    )

@router.post("/api-key/rotate", response_model=UserResponse)
async def rotate_api_key(user_id: str = Depends(verify_api_key)):
    """Rotate API key for current user"""
    db = get_database()

    # verify_api_key now returns user_id instead of api_key
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
async def get_current_user(user_id: str = Depends(verify_api_key)):
    """Get current user information"""
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
