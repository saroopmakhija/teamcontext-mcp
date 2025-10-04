from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import ContextSaveRequest, ContextSearchRequest, ContextResponse
from app.dependencies import verify_api_key
from app.db.mongodb import get_database
from app.services.embedding_service import embedding_service
from datetime import datetime
from bson import ObjectId
from typing import List

router = APIRouter(prefix="/api/v1/context", tags=["context"])

async def get_current_user(user_id: str = Depends(verify_api_key)):
    """Helper to get current user from user_id"""
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def check_project_access(project_id: str, user: dict, db):
    """Check if user has access to project"""
    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if user is owner or contributor
    if project["owner_id"] != user["_id"] and user["_id"] not in project.get("contributors", []):
        raise HTTPException(status_code=403, detail="Access denied to this project")

    return project

@router.post("/save")
async def save_context(
    request: ContextSaveRequest,
    user: dict = Depends(get_current_user)
):
    """Save context with embedding (requires project access)"""
    db = get_database()

    # Verify project access if project_id provided
    if request.project_id:
        await check_project_access(request.project_id, user, db)

    # Generate embedding
    embedding = embedding_service.generate_embedding(request.content)

    # Create context document
    context_doc = {
        "content": request.content,
        "embedding": embedding,
        "metadata": {
            "source": request.source,
            "tags": request.tags,
            "project_id": request.project_id,
            "created_by": str(user["_id"])
        },
        "created_at": datetime.utcnow(),
        "accessed_count": 0
    }

    # Insert into MongoDB
    result = await db.contexts.insert_one(context_doc)

    return {
        "status": "success",
        "context_id": str(result.inserted_id),
        "message": "Context saved successfully"
    }

@router.post("/search", response_model=List[ContextResponse])
async def search_context(
    request: ContextSearchRequest,
    user: dict = Depends(get_current_user)
):
    """Semantic search for context (only searches user's accessible projects)"""
    db = get_database()

    # Get user's accessible projects
    accessible_projects = await db.projects.find({
        "$or": [
            {"owner_id": user["_id"]},
            {"contributors": user["_id"]}
        ]
    }).to_list(length=100)

    accessible_project_ids = [str(p["_id"]) for p in accessible_projects]

    # If project_id specified, verify access
    if request.project_id:
        if request.project_id not in accessible_project_ids:
            raise HTTPException(status_code=403, detail="Access denied to this project")
        # Search only in this project
        filter_query = {"metadata.project_id": request.project_id}
    else:
        # Search in all accessible projects
        filter_query = {"metadata.project_id": {"$in": accessible_project_ids}}

    # Generate query embedding
    query_embedding = embedding_service.generate_embedding(request.query)

    # Get contexts from accessible projects
    cursor = db.contexts.find(filter_query)
    contexts = await cursor.to_list(length=1000)

    # Calculate similarities
    results = []
    for ctx in contexts:
        similarity = embedding_service.calculate_similarity(
            query_embedding,
            ctx["embedding"]
        )

        if similarity >= request.similarity_threshold:
            results.append({
                "id": str(ctx["_id"]),
                "content": ctx["content"],
                "similarity_score": similarity,
                "metadata": ctx["metadata"],
                "created_at": ctx["created_at"]
            })

    # Sort by similarity and limit
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    results = results[:request.limit]

    # Update access count
    for result in results:
        await db.contexts.update_one(
            {"_id": ObjectId(result["id"])},
            {"$inc": {"accessed_count": 1}}
        )

    return results

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "context-api"}
