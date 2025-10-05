from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# Legacy schemas - keeping for backward compatibility
class ContextSaveRequest(BaseModel):
    content: str
    project_id: Optional[str] = None
    tags: Optional[List[str]] = []
    source: str = "api"

class ContextSearchRequest(BaseModel):
    query: str
    project_id: Optional[str] = None
    limit: int = 10
    similarity_threshold: float = 0.01

class ContextResponse(BaseModel):
    id: str
    content: str
    similarity_score: Optional[float] = None
    metadata: dict
    created_at: datetime

# New schemas for chunking workflow
class ChunkInput(BaseModel):
    """Input for chunking service - represents a single chunk of content"""
    content: str
    metadata: Optional[Dict[str, Any]] = {}

class ChunkAndEmbedRequest(BaseModel):
    """Request to chunk content, generate embeddings, and store in vector DB"""
    project_id: str  # REQUIRED: All vectors must be project-specific
    chunks: List[ChunkInput]  # List of pre-chunked content from chunking service
    source: str = "mcp_client"
    tags: Optional[List[str]] = []

class VectorRetrievalRequest(BaseModel):
    """Request to retrieve similar vectors from project-specific vector DB"""
    project_id: str  # REQUIRED: Only search within this project
    query: str  # The query to search for
    limit: int = 10
    similarity_threshold: float = 0.01

class VectorRetrievalResponse(BaseModel):
    """Response with similar chunks from vector DB"""
    chunk_id: str
    content: str
    similarity_score: float
    metadata: Dict[str, Any]
    created_at: datetime
