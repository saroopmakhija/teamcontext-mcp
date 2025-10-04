from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str
    description: str
    owner_id: str

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    chunks: List[str]  # List of chunk IDs
    owner_id: str
    owner_name: str
    contributors: List[str]  # List of user IDs
    created_at: datetime
    updated_at: datetime

class ContributorAdd(BaseModel):
    user_id: str  # User ID to add as contributor
