from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ContextSaveRequest(BaseModel):
    content: str
    project_id: Optional[str] = None
    tags: Optional[List[str]] = []
    source: str = "api"

class ContextSearchRequest(BaseModel):
    query: str
    project_id: Optional[str] = None
    limit: int = 10
    similarity_threshold: float = 0.5

class ContextResponse(BaseModel):
    id: str
    content: str
    similarity_score: Optional[float] = None
    metadata: dict
    created_at: datetime
