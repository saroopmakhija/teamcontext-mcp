from fastmcp.server import FastMCP
from mcp.api import make_api_call

# Backend API configuration
BACKEND_URL = "http://localhost:8000"
API_KEY = "hackathon-demo-key-2025"

mcp = FastMCP(name="TeamContext MCP Client")

@mcp.tool(name="save_context", description="Save context to the shared knowledge base")
async def save_context(content: str, tags: list[str] = None, project_id: str = None) -> dict:
    """
    Save context to TeamContext backend for sharing across agents

    Args:
        content: The context/information to save
        tags: Optional tags for categorization
        project_id: Optional project ID to associate context with
    """
    response = await make_api_call(
        method="POST",
        endpoint=f"{BACKEND_URL}/api/v1/context/save",
        data={
            "content": content,
            "tags": tags or [],
            "project_id": project_id,
            "source": "claude"
        }
    )
    return response

@mcp.tool(name="search_context", description="Search for relevant context from the knowledge base")
async def search_context(query: str, limit: int = 10, project_id: str = None) -> dict:
    """
    Search for relevant context using semantic search

    Args:
        query: What to search for
        limit: Maximum number of results (default 10)
        project_id: Optional project ID to search within
    """
    response = await make_api_call(
        method="POST",
        endpoint=f"{BACKEND_URL}/api/v1/context/search",
        data={
            "query": query,
            "limit": limit,
            "project_id": project_id,
            "similarity_threshold": 0.5
        }
    )
    return response

@mcp.tool(name="health_check", description="Check if the backend API is healthy")
async def health_check() -> dict:
    """Check backend API health status"""
    response = await make_api_call(
        method="GET",
        endpoint=f"{BACKEND_URL}/health",
    )
    return response
