from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import (
    ContextSaveRequest, ContextSearchRequest, ContextResponse,
    ChunkAndEmbedRequest, VectorRetrievalRequest, VectorRetrievalResponse
)
from app.dependencies import verify_jwt_or_api_key
from app.db.mongodb import get_database
from app.services.embedding_service import embedding_service
from datetime import datetime
from bson import ObjectId
from typing import List

router = APIRouter(prefix="/api/v1/context", tags=["context"])

async def get_current_user(user_id: str = Depends(verify_jwt_or_api_key)):
    """Helper to get current user from user_id (JWT or API key auth)"""
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
        # Search in all accessible projects + user's own contexts without project
        filter_query = {
            "$or": [
                {"metadata.project_id": {"$in": accessible_project_ids}},
                {"metadata.created_by": str(user["_id"]), "metadata.project_id": None}
            ]
        }

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


@router.get("/{context_id}")
async def get_context(context_id: str):
    """Get context by id"""
    db = get_database()
    context = await db.contexts.find_one({"_id": ObjectId(context_id)})
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")
    return context["content"]

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "context-api"}


# NEW ENDPOINTS FOR MCP CLIENT WORKFLOW

@router.post("/chunk-and-embed")
async def chunk_and_embed(
    request: ChunkAndEmbedRequest,
    user: dict = Depends(get_current_user)
):
    """
    MCP Client Workflow Step 1: Receive pre-chunked content from chunking service,
    generate embeddings, and store in project-specific vector DB.

    Flow:
    1. MCP Client calls chunking service (external/friend's service)
    2. Chunking service returns chunks
    3. MCP Client calls THIS endpoint with chunks
    4. This endpoint generates embeddings via Gemini
    5. Stores vectors in MongoDB with project_id isolation
    """
    db = get_database()

    # Verify user has access to this project
    await check_project_access(request.project_id, user, db)

    if not request.chunks or len(request.chunks) == 0:
        raise HTTPException(status_code=400, detail="No chunks provided")

    # Extract just the text content for batch embedding
    chunk_texts = [chunk.content for chunk in request.chunks]

    print(f"🔄 Generating embeddings for {len(chunk_texts)} chunks...")

    # Generate embeddings in batch (efficient!)
    embeddings = embedding_service.embed_batch(chunk_texts)

    print(f"✅ Generated {len(embeddings)} embeddings with {len(embeddings[0])} dimensions each")

    # Prepare documents for insertion
    vector_docs = []
    for i, (chunk, embedding) in enumerate(zip(request.chunks, embeddings)):
        doc = {
            "content": chunk.content,
            "embedding": embedding,
            "metadata": {
                "project_id": request.project_id,  # PROJECT-SPECIFIC ISOLATION
                "created_by": str(user["_id"]),
                "source": request.source,
                "tags": request.tags,
                "chunk_index": i,
                **chunk.metadata  # Include any custom metadata from chunking service
            },
            "created_at": datetime.utcnow(),
            "accessed_count": 0
        }
        vector_docs.append(doc)

    # Batch insert into MongoDB
    result = await db.contexts.insert_many(vector_docs)

    print(f"✅ Stored {len(result.inserted_ids)} vectors in project {request.project_id}")

    return {
        "status": "success",
        "project_id": request.project_id,
        "chunks_processed": len(chunk_texts),
        "vectors_stored": len(result.inserted_ids),
        "embedding_dimensions": len(embeddings[0]),
        "vector_ids": [str(id) for id in result.inserted_ids]
    }


@router.post("/retrieve", response_model=List[VectorRetrievalResponse])
async def retrieve_vectors(
    request: VectorRetrievalRequest,
    user: dict = Depends(get_current_user)
):
    """
    MCP Client Workflow Step 2: Retrieve similar vectors from project-specific vector DB.

    Flow:
    1. MCP Client calls THIS endpoint with query + project_id
    2. Generate embedding for query
    3. Search ONLY within specified project (project isolation)
    4. Calculate cosine similarity
    5. Return top-k most similar chunks

    IMPORTANT: Only searches within the specified project_id for data isolation
    """
    db = get_database()

    # Verify user has access to this project
    await check_project_access(request.project_id, user, db)

    print(f"🔍 Searching project {request.project_id} for: '{request.query}'")

    # Generate query embedding
    query_embedding = embedding_service.generate_embedding(request.query)

    # PROJECT-SPECIFIC FILTER: Only search within this project
    filter_query = {"metadata.project_id": request.project_id}

    # Get all vectors from THIS PROJECT ONLY
    cursor = db.contexts.find(filter_query)
    contexts = await cursor.to_list(length=10000)  # Adjust limit based on project size

    print(f"📊 Found {len(contexts)} vectors in project {request.project_id}")

    if len(contexts) == 0:
        return []

    # Calculate similarities
    results = []
    for ctx in contexts:
        similarity = embedding_service.calculate_similarity(
            query_embedding,
            ctx["embedding"]
        )

        if similarity >= request.similarity_threshold:
            results.append({
                "chunk_id": str(ctx["_id"]),
                "content": ctx["content"],
                "similarity_score": similarity,
                "metadata": ctx["metadata"],
                "created_at": ctx["created_at"]
            })

    # Sort by similarity (highest first) and limit
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    results = results[:request.limit]

    print(f"✅ Returning {len(results)} results above threshold {request.similarity_threshold}")

    # Update access count for retrieved chunks
    for result in results:
        await db.contexts.update_one(
            {"_id": ObjectId(result["chunk_id"])},
            {"$inc": {"accessed_count": 1}}
        )

    return results
