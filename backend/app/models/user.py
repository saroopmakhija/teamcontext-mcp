from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    api_key: str  # Only shown on registration/rotation
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class APIKeyRotate(BaseModel):
    pass  # No fields needed, just triggers rotation

class APIKeyCreate(BaseModel):
    name: str  # Optional name for the API key

class APIKeyResponse(BaseModel):
    id: str
    name: str
    key: str  # Only shown once on creation
    created_at: datetime
