from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ChunkCreate(BaseModel):
    content: str
    project_id: str
    user_id: str
    metadata: Optional[Dict[str, Any]] = {}

class ChunkUpdate(BaseModel):
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ChunkResponse(BaseModel):
    chunk_id: str
    content: str
    project_id: str
    user_id: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class ChunkSearchRequest(BaseModel):
    query: str
    project_id: Optional[str] = None
    limit: int = 10
    similarity_threshold: float = 0.5
