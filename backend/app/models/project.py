from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str
    description: str

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    owner_id: str
    owner_name: str
    contributors: List[dict]  # List of {id, name, email}
    created_at: datetime
    updated_at: datetime

class ContributorAdd(BaseModel):
    email: str  # Email of user to add
