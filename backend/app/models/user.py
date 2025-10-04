from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    api_keys: List[str]  # List of API keys
    projects: List[str]  # List of project IDs
    created_at: datetime
    updated_at: datetime

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
