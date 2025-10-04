from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    api_key: str
    created_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class APIKeyRotate(BaseModel):
    pass  # No fields needed, just triggers rotation
