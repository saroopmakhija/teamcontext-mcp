# TeamContext Backend Architecture

## Tech Stack - High Performance, Production Ready

### Core Framework
- **FastAPI** (Async Python Web Framework)
  - Automatic OpenAPI docs
  - Native async/await support
  - Pydantic validation
  - High performance (comparable to NodeJS/Go)
  - Built-in dependency injection

### Database Layer
- **MongoDB** (Primary Database)
  - User accounts, projects, permissions
  - Flexible schema for rapid iteration
  - Motor driver for async operations

- **MongoDB Atlas Vector Search** (Vector Store)
  - Native vector search capabilities
  - No additional service needed
  - Semantic search for context retrieval
  - Efficient similarity search with HNSW indexing

### Authentication & Security
- **JWT (JSON Web Tokens)**
  - Stateless authentication
  - PyJWT library
  - Short-lived access tokens (15min)
  - Longer refresh tokens (7 days)

- **API Keys**
  - Generated per user for MCP clients
  - Used in Authorization header
  - Can be rotated/revoked

- **PassLib + Bcrypt**
  - Secure password hashing
  - Industry standard

### Performance & Optimization
- **Motor** (Async MongoDB Driver)
  - Non-blocking I/O
  - Connection pooling
  - Efficient batch operations

- **Uvicorn** (ASGI Server)
  - High-performance async server
  - HTTP/1.1 and WebSocket support

- **Redis** (Optional - Phase 2)
  - API key validation caching
  - Rate limiting
  - Session management

### Additional Libraries
- **Pydantic** - Data validation and settings
- **python-multipart** - File upload support (for codebase scanning)
- **sentence-transformers** - Generate embeddings for context
- **tiktoken** - Token counting for chunking and cost analytics
- **httpx** - Async HTTP client for external integrations (Jira, etc.)

---

## Data Models

### Users Collection
```python
{
  "_id": ObjectId,
  "email": str,  # Unique, indexed
  "name": str,
  "hashed_password": str,
  "api_key": str,  # Unique, indexed, for MCP auth
  "api_key_created_at": datetime,  # For rotation tracking
  "refresh_tokens": [str],  # Active refresh tokens (hashed)
  "integrations": {
    "jira": {
      "enabled": bool,
      "site_url": str?,
      "access_token": str?,  # Encrypted
      "refresh_token": str?,  # Encrypted
      "expires_at": datetime?
    }
  },
  "created_at": datetime,
  "updated_at": datetime,
  "is_active": bool,
  "email_verified": bool
}
```

### Projects Collection
```python
{
  "_id": ObjectId,
  "name": str,
  "description": str,  # For semantic search
  "owner_id": ObjectId,  # Ref to Users
  "contributors": [ObjectId],  # Array of user_ids
  "settings": {
    "visibility": "private" | "team",
    "auto_scan": bool,
    "embedding_model": str
  },
  "created_at": datetime,
  "updated_at": datetime
}
```

### Context Collection (Vector Store)
```python
{
  "_id": ObjectId,
  "project_id": ObjectId,  # Indexed
  "content": str,  # The actual context/code
  "embedding": [float],  # 384 or 768 dim vector (Atlas Vector Search)
  "token_count": int,  # Calculated via tiktoken
  "metadata": {
    "created_by": ObjectId,
    "source": "manual" | "codebase_scan" | "claude" | "cursor" | "chatgpt" | "jira",
    "file_path": str?,  # If from codebase
    "language": str?,
    "tags": [str],
    "chunk_index": int?,  # If part of larger file
    "parent_id": ObjectId?,  # If chunked from larger context
    "jira_issue_key": str?  # If from Jira integration
  },
  "created_at": datetime,
  "accessed_count": int,  # Track usage for analytics
  "last_accessed": datetime?
}
```

### Analytics Collection (Usage & Cost Tracking)
```python
{
  "_id": ObjectId,
  "user_id": ObjectId,  # Indexed
  "project_id": ObjectId?,  # Indexed
  "event_type": "context_save" | "context_retrieve" | "scan_codebase" | "jira_sync",
  "timestamp": datetime,  # Indexed
  "metrics": {
    "tokens_saved": int,  # Context provided to LLM
    "tokens_avoided": int,  # Tokens NOT pasted (cost saved)
    "contexts_retrieved": int,
    "api_calls_made": int,
    "processing_time_ms": float
  },
  "cost_impact": {
    "tokens_at_cost": float,  # Cost per 1M tokens
    "estimated_savings_usd": float
  }
}
```

### Jira Integration Cache (Optional)
```python
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "project_id": ObjectId,
  "jira_issue_key": str,  # Indexed
  "issue_data": dict,  # Cached Jira issue data
  "synced_to_context": bool,
  "last_synced": datetime,
  "ttl": datetime  # Auto-delete after expiry
}
```

### Indexes for Performance
```python
# Users
- email: unique
- api_key: unique, sparse
- integrations.jira.enabled: 1

# Projects
- owner_id: 1
- contributors: 1
- description: text  # Text search

# Context
- project_id: 1
- created_at: -1
- embedding: vector (Atlas Vector Search Index)
- metadata.jira_issue_key: 1, sparse
- accessed_count: -1  # For popular context queries

# Analytics
- user_id: 1
- project_id: 1
- timestamp: -1  # Time-series queries
- event_type: 1

# Jira Cache
- jira_issue_key: 1, unique
- ttl: 1  # TTL index for auto-cleanup
```

---

## API Endpoints

### Authentication & User Management
```
POST   /api/v1/auth/register          # Register new user
POST   /api/v1/auth/login             # Login (returns JWT + API key)
POST   /api/v1/auth/refresh           # Refresh JWT token
POST   /api/v1/auth/logout            # Invalidate refresh token
GET    /api/v1/users/me               # Get current user info
POST   /api/v1/users/me/api-key/rotate # Generate new API key
```

### Project Management
```
GET    /api/v1/projects               # List user's projects (owned + contributor)
POST   /api/v1/projects               # Create new project
GET    /api/v1/projects/{id}          # Get project details
PUT    /api/v1/projects/{id}          # Update project
DELETE /api/v1/projects/{id}          # Delete project (owner only)
```

### Collaboration
```
POST   /api/v1/projects/{id}/contributors              # Add contributor
DELETE /api/v1/projects/{id}/contributors/{user_id}   # Remove contributor
GET    /api/v1/projects/{id}/contributors              # List contributors
```

### Context Operations (Core MCP Integration)
```
POST   /api/v1/context/save           # Save context to project
  Body: {
    "content": str,
    "project_id": str?,  # Optional, can infer
    "metadata": {
      "source": str,
      "tags": [str]?,
      "file_path": str?
    }
  }

POST   /api/v1/context/search         # Semantic search for context
  Body: {
    "query": str,
    "project_ids": [str]?,  # If null, search all accessible
    "limit": int = 10,
    "similarity_threshold": float = 0.7
  }
  Returns: [{
    "content": str,
    "similarity_score": float,
    "metadata": {...},
    "project_name": str
  }]

GET    /api/v1/context/{id}           # Get specific context
DELETE /api/v1/context/{id}           # Delete context
GET    /api/v1/projects/{id}/context  # List all context in project
```

### Codebase Scanning (RAG Feature)
```
POST   /api/v1/projects/{id}/scan     # Scan and ingest codebase
  Body: {
    "files": [FileUpload],  # Or
    "git_url": str?,
    "branch": str?,
    "file_patterns": [str]?,  # e.g., ["*.py", "*.ts"]
    "chunk_size": int = 1000,
    "chunk_overlap": int = 200
  }

GET    /api/v1/projects/{id}/scan/status/{job_id}  # Check scan status
```

### Jira Integration
```
POST   /api/v1/integrations/jira/connect       # Connect Jira account (OAuth)
DELETE /api/v1/integrations/jira/disconnect    # Disconnect Jira
GET    /api/v1/integrations/jira/status        # Check connection status

POST   /api/v1/jira/sync                       # Sync Jira issues to context
  Body: {
    "project_id": str,
    "jql_query": str?,  # Optional JQL filter
    "issue_keys": [str]?  # Or specific issues
  }

GET    /api/v1/jira/issues/{issue_key}         # Fetch specific issue
POST   /api/v1/jira/search                     # Search Jira issues
  Body: {
    "jql": str,
    "max_results": int = 50
  }
```

### Analytics & Observability
```
GET    /api/v1/analytics/cost-savings          # Get cost savings report
  Query: {
    "user_id": str?,
    "project_id": str?,
    "start_date": datetime?,
    "end_date": datetime?,
    "group_by": "day" | "week" | "month"
  }
  Returns: {
    "total_tokens_saved": int,
    "total_tokens_avoided": int,
    "estimated_cost_usd": float,
    "estimated_savings_usd": float,
    "breakdown": [{
      "period": str,
      "tokens_saved": int,
      "savings_usd": float
    }]
  }

GET    /api/v1/analytics/usage                 # Usage statistics
  Returns: {
    "contexts_created": int,
    "contexts_retrieved": int,
    "projects_count": int,
    "top_projects": [{ "name": str, "usage_count": int }],
    "sources_breakdown": { "claude": int, "cursor": int, ... }
  }

GET    /api/v1/analytics/context-insights      # Context usage insights
  Returns: {
    "most_accessed_contexts": [{ "content": str, "access_count": int }],
    "avg_tokens_per_context": float,
    "total_storage_mb": float
  }

GET    /api/v1/health                          # Health check
GET    /api/v1/metrics                         # Prometheus-style metrics
```

---

## Authentication Flow

### For Web Users (JWT)
1. User registers/logs in � Receives JWT access token + refresh token
2. Access token used for API calls (expires in 15 min)
3. When expired, use refresh token to get new access token
4. User also receives persistent API key for MCP clients

### For MCP Clients (API Key)
1. User copies API key from web dashboard
2. MCP client includes API key in header: `Authorization: Bearer <api_key>`
3. Backend validates API key on each request
4. Fast validation (cached in Redis in Phase 2)

---

## Authentication Edge Cases & Error Handling

### Edge Cases Covered

**1. API Key Rotation**
- Old API key remains valid for 24 hours after rotation
- Grace period allows time to update MCP clients
- Multiple MCP clients can use same API key

**2. Concurrent Refresh Token Usage**
- Refresh tokens are single-use
- If used concurrently, first request wins
- Other requests get 401, must re-authenticate
- Mitigate with token reuse detection (5-second window)

**3. Account Deactivation**
- API keys immediately invalidated
- Active JWT tokens invalidated via blacklist (Redis)
- Refresh tokens cleared from database

**4. Password Reset**
- All refresh tokens invalidated
- API key optionally rotated (user choice)
- User must re-login on all devices

**5. Email Verification**
- Unverified users have limited access
- Can save context but not retrieve
- Or block all access until verified (configurable)

**6. Rate Limiting**
- Per API key: 100 req/min (burst: 120)
- Per user IP: 200 req/min
- Per endpoint: context/search limited to 30 req/min

**7. Deleted Projects**
- Soft delete with 30-day retention
- Context marked as inaccessible
- Owner can restore within 30 days

**8. Removed Contributors**
- Lose access immediately
- Cached data in their MCP cleared on next request
- No retroactive data deletion

**9. Jira Token Expiry**
- Auto-refresh using refresh token
- If refresh fails, disable integration
- Notify user via webhook/email

**10. Large Context Handling**
- Max context size: 100K tokens
- Auto-chunking if exceeded
- Warning if single context > 10K tokens

### Error Response Format
```json
{
  "error": {
    "code": "INVALID_API_KEY",
    "message": "The API key provided is invalid or has been revoked",
    "details": {
      "reason": "revoked",
      "revoked_at": "2025-01-15T10:30:00Z"
    },
    "request_id": "req_abc123xyz"
  }
}
```

### Standard Error Codes
```python
# Authentication
- INVALID_CREDENTIALS (401)
- INVALID_API_KEY (401)
- TOKEN_EXPIRED (401)
- TOKEN_REVOKED (401)
- EMAIL_NOT_VERIFIED (403)

# Authorization
- INSUFFICIENT_PERMISSIONS (403)
- PROJECT_ACCESS_DENIED (403)
- RATE_LIMIT_EXCEEDED (429)

# Validation
- INVALID_INPUT (400)
- MISSING_REQUIRED_FIELD (400)
- CONTEXT_TOO_LARGE (413)

# Resources
- RESOURCE_NOT_FOUND (404)
- PROJECT_NOT_FOUND (404)
- CONTEXT_NOT_FOUND (404)

# Integration
- JIRA_CONNECTION_FAILED (502)
- JIRA_AUTH_EXPIRED (401)
- JIRA_RATE_LIMIT (429)

# System
- INTERNAL_SERVER_ERROR (500)
- DATABASE_ERROR (500)
- EMBEDDING_GENERATION_FAILED (500)
```

---

## Context Retrieval Strategy (Semantic Search)

### Two-Level Search (As per CLAUDE.md)

**Level 1: Project Discovery**
```python
async def find_relevant_projects(query: str, user_id: ObjectId, k: int = 3):
    """
    Search project descriptions to find relevant projects
    """
    # Generate embedding for query
    query_embedding = generate_embedding(query)

    # Get all accessible projects
    accessible_projects = await get_user_projects(user_id)

    # Vector search on project descriptions
    relevant_projects = await vector_search(
        collection="projects",
        field="description_embedding",  # Pre-computed
        query_vector=query_embedding,
        filter={"_id": {"$in": accessible_projects}},
        limit=k
    )

    return relevant_projects
```

**Level 2: Context Retrieval**
```python
async def get_relevant_context(query: str, project_ids: List[ObjectId], k: int = 10):
    """
    Search within project contexts for most relevant information
    """
    query_embedding = generate_embedding(query)

    # Vector search in context collection
    contexts = await vector_search(
        collection="context",
        field="embedding",
        query_vector=query_embedding,
        filter={"project_id": {"$in": project_ids}},
        limit=k,
        similarity_threshold=0.7
    )

    return contexts
```

### Combined Flow
```python
async def smart_context_retrieval(query: str, user_id: ObjectId):
    # Step 1: Find relevant projects
    projects = await find_relevant_projects(query, user_id, k=3)

    # Step 2: Search within those projects
    contexts = await get_relevant_context(
        query,
        [p["_id"] for p in projects],
        k=10
    )

    return {
        "relevant_projects": projects,
        "contexts": contexts
    }
```

---

## Codebase Scanning & RAG Pipeline

### Chunking Strategy
```python
def chunk_code(content: str, file_path: str, chunk_size: int = 1000):
    """
    Intelligent code chunking:
    - Respect function/class boundaries
    - Maintain context with overlap
    - Include file path in metadata
    """
    # Use AST parsing for language-aware chunking
    # For unsupported languages, fallback to semantic chunking

    chunks = []
    # Implementation depends on file type
    # Python: ast.parse
    # TypeScript/JS: ts-morph or simple regex
    # Others: semantic text splitting

    return chunks
```

### Embedding Generation
```python
from sentence_transformers import SentenceTransformer

# Use all-MiniLM-L6-v2 (384 dim) or all-mpnet-base-v2 (768 dim)
model = SentenceTransformer('all-MiniLM-L6-v2')

async def generate_embedding(text: str):
    embedding = model.encode(text)
    return embedding.tolist()
```

### Scan Workflow
```
1. Receive files/git repo
2. Filter by file patterns (*.py, *.ts, etc.)
3. Parse and chunk each file
4. Generate embeddings for each chunk
5. Store in Context collection with metadata
6. Return job status
```

---

## Cost Analytics & Token Tracking

### How Cost Savings are Calculated

**Concept**: Every time context is retrieved and provided to an LLM, we calculate the "cost avoided" by not having the user manually paste that content.

```python
import tiktoken

# Token pricing (as of 2025, update dynamically)
MODEL_PRICING = {
    "claude-3-opus": {"input": 15.00, "output": 75.00},  # per 1M tokens
    "claude-3-sonnet": {"input": 3.00, "output": 15.00},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-4o": {"input": 5.00, "output": 15.00},
}

async def calculate_cost_savings(context_content: str, model: str = "claude-3-sonnet"):
    """
    Calculate the cost savings from using stored context
    """
    # Count tokens using tiktoken
    encoding = tiktoken.encoding_for_model("gpt-4")  # Use as proxy
    token_count = len(encoding.encode(context_content))

    # Calculate cost if user had to paste this manually
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["claude-3-sonnet"])
    cost_per_token = pricing["input"] / 1_000_000
    cost_saved_usd = token_count * cost_per_token

    return {
        "tokens_saved": token_count,
        "cost_saved_usd": cost_saved_usd,
        "model": model
    }

async def track_context_retrieval(user_id, project_id, contexts_retrieved):
    """
    Track analytics when context is retrieved via MCP
    """
    total_tokens = sum(ctx.token_count for ctx in contexts_retrieved)

    # Log analytics event
    analytics_event = {
        "user_id": user_id,
        "project_id": project_id,
        "event_type": "context_retrieve",
        "timestamp": datetime.utcnow(),
        "metrics": {
            "tokens_saved": total_tokens,
            "tokens_avoided": total_tokens,  # Same in this case
            "contexts_retrieved": len(contexts_retrieved),
            "api_calls_made": 1
        },
        "cost_impact": await calculate_cost_savings(
            "\n".join(ctx.content for ctx in contexts_retrieved)
        )
    }

    await analytics_collection.insert_one(analytics_event)
```

### Analytics Dashboard Queries

**Monthly Cost Savings**
```python
async def get_monthly_savings(user_id: ObjectId, month: int, year: int):
    """
    Aggregate cost savings for a specific month
    """
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)

    pipeline = [
        {
            "$match": {
                "user_id": user_id,
                "timestamp": {"$gte": start_date, "$lt": end_date}
            }
        },
        {
            "$group": {
                "_id": None,
                "total_tokens_saved": {"$sum": "$metrics.tokens_saved"},
                "total_savings_usd": {"$sum": "$cost_impact.cost_saved_usd"},
                "total_contexts": {"$sum": "$metrics.contexts_retrieved"}
            }
        }
    ]

    result = await analytics_collection.aggregate(pipeline).to_list(1)
    return result[0] if result else {}
```

---

## Jira Integration Implementation

### OAuth 2.0 Flow with Jira

**Step 1: Initiate Connection**
```python
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name='jira',
    client_id=settings.JIRA_CLIENT_ID,
    client_secret=settings.JIRA_CLIENT_SECRET,
    authorize_url='https://auth.atlassian.com/authorize',
    access_token_url='https://auth.atlassian.com/oauth/token',
    client_kwargs={'scope': 'read:jira-work write:jira-work offline_access'}
)

@app.get("/api/v1/integrations/jira/connect")
async def connect_jira(request: Request):
    """
    Redirect user to Jira OAuth consent screen
    """
    redirect_uri = request.url_for('jira_callback')
    return await oauth.jira.authorize_redirect(request, redirect_uri)

@app.get("/api/v1/integrations/jira/callback")
async def jira_callback(request: Request, current_user: User = Depends(get_current_user)):
    """
    Handle OAuth callback and store tokens
    """
    token = await oauth.jira.authorize_access_token(request)

    # Store encrypted tokens in user document
    await users_collection.update_one(
        {"_id": current_user.id},
        {
            "$set": {
                "integrations.jira": {
                    "enabled": True,
                    "access_token": encrypt(token['access_token']),
                    "refresh_token": encrypt(token['refresh_token']),
                    "expires_at": datetime.utcnow() + timedelta(seconds=token['expires_in'])
                }
            }
        }
    )

    return {"status": "connected"}
```

### Syncing Jira Issues to Context

```python
async def sync_jira_issues(project_id: str, jql_query: str, user: User):
    """
    Fetch Jira issues and convert to context
    """
    # Get Jira access token
    jira_config = user.integrations.get('jira', {})
    if not jira_config.get('enabled'):
        raise HTTPException(400, "Jira not connected")

    access_token = decrypt(jira_config['access_token'])

    # Fetch issues from Jira API
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.atlassian.com/ex/jira/{cloudId}/rest/api/3/search",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"jql": jql_query, "maxResults": 50}
        )
        issues = response.json()['issues']

    # Convert each issue to context
    contexts = []
    for issue in issues:
        content = format_jira_issue_as_context(issue)
        embedding = await generate_embedding(content)
        token_count = len(tiktoken.encoding_for_model("gpt-4").encode(content))

        context = {
            "project_id": ObjectId(project_id),
            "content": content,
            "embedding": embedding,
            "token_count": token_count,
            "metadata": {
                "created_by": user.id,
                "source": "jira",
                "jira_issue_key": issue['key'],
                "tags": ["jira", issue['fields']['issuetype']['name'].lower()]
            },
            "created_at": datetime.utcnow(),
            "accessed_count": 0
        }
        contexts.append(context)

    # Bulk insert
    if contexts:
        await context_collection.insert_many(contexts)

    return {"synced_count": len(contexts)}

def format_jira_issue_as_context(issue: dict) -> str:
    """
    Format Jira issue into readable context for LLMs
    """
    fields = issue['fields']

    return f"""
# {issue['key']}: {fields['summary']}

**Type**: {fields['issuetype']['name']}
**Status**: {fields['status']['name']}
**Priority**: {fields.get('priority', {}).get('name', 'N/A')}
**Assignee**: {fields.get('assignee', {}).get('displayName', 'Unassigned')}

## Description
{fields.get('description', 'No description provided')}

## Comments
{format_comments(fields.get('comment', {}).get('comments', []))}

**Link**: {issue['self']}
**Created**: {fields['created']}
**Updated**: {fields['updated']}
""".strip()
```

---

## Performance Considerations

### Database Optimization
- **Connection Pooling**: Motor handles this automatically
- **Batch Inserts**: Use `insert_many()` for bulk context saves
- **Indexes**: Proper indexing on frequently queried fields
- **Vector Search**: Atlas Vector Search uses HNSW for fast ANN

### API Optimization
- **Async/Await**: Non-blocking I/O throughout
- **Response Models**: Pydantic serialization
- **Pagination**: Cursor-based for large result sets
- **Caching**: Redis for API key validation (Phase 2)

### Scalability
- **Horizontal Scaling**: FastAPI + MongoDB both scale horizontally
- **Background Tasks**: Use FastAPI BackgroundTasks for scans
- **Queue System**: Optional Celery/RQ for heavy operations (Phase 2)

---

## Security Best Practices

1. **Password Hashing**: Bcrypt with salt
2. **JWT Secrets**: Store in environment variables
3. **API Key Rotation**: Support key rotation without downtime
4. **Input Validation**: Pydantic models for all inputs
5. **Rate Limiting**: Implement per API key (Phase 2)
6. **CORS**: Configure properly for frontend
7. **HTTPS Only**: Enforce in production
8. **Secrets Management**: Use environment variables, never commit

---

## Development Phases

### Phase 1: Core MVP (Week 1-2)
- [ ] FastAPI setup with Uvicorn
- [ ] MongoDB connection with Motor
- [ ] User registration/login (JWT)
- [ ] API key generation and validation
- [ ] Project CRUD
- [ ] Contributor management
- [ ] Basic context save/retrieve

### Phase 2: Vector Search & Analytics (Week 2-3)
- [ ] MongoDB Atlas Vector Search setup
- [ ] Embedding generation integration
- [ ] Semantic search endpoints
- [ ] Two-level context retrieval
- [ ] Token counting with tiktoken
- [ ] Analytics collection and tracking
- [ ] Cost savings calculation

### Phase 3: Integrations & RAG (Week 3-4)
- [ ] File upload handling
- [ ] Code chunking logic
- [ ] Background job processing
- [ ] Scan status tracking
- [ ] Jira OAuth integration
- [ ] Jira issue syncing to context

### Phase 4: Observability & Polish (Week 4-5)
- [ ] Analytics dashboard endpoints
- [ ] Cost savings reports
- [ ] Usage insights
- [ ] Redis caching for API keys
- [ ] Rate limiting per endpoint
- [ ] Comprehensive error handling

### Phase 5: Production Ready (Week 5+)
- [ ] Monitoring/logging (structured logs)
- [ ] Frontend dashboard
- [ ] API documentation (OpenAPI)
- [ ] Deployment setup (Docker)
- [ ] CI/CD pipeline

---

## Environment Variables

```bash
# App
APP_NAME=teamcontext-api
ENVIRONMENT=development
DEBUG=True

# MongoDB
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DB_NAME=teamcontext

# JWT
JWT_SECRET_KEY=<openssl rand -hex 32>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API Keys
API_KEY_LENGTH=32

# Embedding
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Jira Integration
JIRA_CLIENT_ID=your_jira_client_id
JIRA_CLIENT_SECRET=your_jira_client_secret
JIRA_REDIRECT_URI=http://localhost:8000/api/v1/integrations/jira/callback

# Encryption (for storing Jira tokens)
ENCRYPTION_KEY=<openssl rand -hex 32>

# Analytics
DEFAULT_LLM_MODEL=claude-3-sonnet  # For cost calculations
ENABLE_ANALYTICS=True
```

---

## MCP Server Integration Points

The MCP server (`mcp/server.py`) will make HTTP requests to these endpoints:

### MCP Tool: `get_relevant_context`
```python
@mcp.tool(name="get_relevant_context")
async def get_relevant_context(query: str, project_id: str = None) -> dict:
    """
    Search for relevant context across projects
    """
    response = await make_api_call(
        method="POST",
        endpoint="/api/v1/context/search",
        data={
            "query": query,
            "project_ids": [project_id] if project_id else None
        }
    )
    return response
```

### MCP Tool: `save_to_context`
```python
@mcp.tool(name="save_to_context")
async def save_to_context(content: str, project_id: str = None, tags: List[str] = None) -> dict:
    """
    Save context to a project
    """
    response = await make_api_call(
        method="POST",
        endpoint="/api/v1/context/save",
        data={
            "content": content,
            "project_id": project_id,
            "metadata": {
                "source": "claude",  # or cursor, chatgpt
                "tags": tags or []
            }
        }
    )
    return response
```

### MCP Tool: `scan_codebase`
```python
@mcp.tool(name="scan_codebase")
async def scan_codebase(project_id: str, files: List[str]) -> dict:
    """
    Scan and ingest codebase into project
    """
    response = await make_api_call(
        method="POST",
        endpoint=f"/api/v1/projects/{project_id}/scan",
        data={
            "files": files,
            "chunk_size": 1000
        }
    )
    return response
```

### MCP Tool: `sync_jira_to_context`
```python
@mcp.tool(name="sync_jira_to_context")
async def sync_jira_to_context(
    project_id: str,
    jql_query: str = None,
    issue_keys: List[str] = None
) -> dict:
    """
    Sync Jira issues to project context
    """
    response = await make_api_call(
        method="POST",
        endpoint="/api/v1/jira/sync",
        data={
            "project_id": project_id,
            "jql_query": jql_query,
            "issue_keys": issue_keys
        }
    )
    return response
```

### MCP Tool: `get_cost_savings`
```python
@mcp.tool(name="get_cost_savings")
async def get_cost_savings(
    project_id: str = None,
    days: int = 30
) -> dict:
    """
    Get cost savings report for the user
    """
    import datetime
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(days=days)

    response = await make_api_call(
        method="GET",
        endpoint="/api/v1/analytics/cost-savings",
        params={
            "project_id": project_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "group_by": "day"
        }
    )
    return response
```

---

## Why This Stack?

### FastAPI
- **Fastest Python framework** for APIs
- Async-first design matches use case
- Automatic API docs (OpenAPI/Swagger)
- Type safety with Pydantic

### MongoDB + Atlas Vector Search
- **Single database** for both relational and vector data
- No need for separate Pinecone/Weaviate
- Scales horizontally
- Managed service (Atlas) handles complexity
- Native vector search with HNSW indexing

### Motor
- **Official async driver** for MongoDB
- Non-blocking I/O critical for performance
- Connection pooling built-in
- Production tested

### JWT + API Keys Hybrid
- **JWT for web users** - stateless, scalable
- **API Keys for MCP** - simple, persistent
- Best of both worlds

### Sentence Transformers
- **State-of-the-art embeddings** with small models
- Fast inference on CPU
- No external API calls needed
- Can upgrade to OpenAI embeddings later

---

## Implementation Best Practices

### 1. Project Structure
```
teamcontext-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Settings & environment variables
│   ├── dependencies.py         # Shared dependencies (auth, etc.)
│   │
│   ├── models/                 # Pydantic models
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── context.py
│   │   └── analytics.py
│   │
│   ├── routers/                # API route handlers
│   │   ├── auth.py
│   │   ├── projects.py
│   │   ├── context.py
│   │   ├── jira.py
│   │   └── analytics.py
│   │
│   ├── services/               # Business logic
│   │   ├── auth_service.py
│   │   ├── context_service.py
│   │   ├── embedding_service.py
│   │   ├── jira_service.py
│   │   └── analytics_service.py
│   │
│   ├── db/                     # Database utilities
│   │   ├── mongodb.py          # Motor client setup
│   │   ├── repositories/       # Data access layer
│   │   └── migrations/         # Schema migrations
│   │
│   └── utils/
│       ├── encryption.py       # Token encryption
│       ├── token_counter.py    # Tiktoken wrapper
│       └── error_handlers.py   # Custom exceptions
│
├── tests/
├── alembic/                    # Optional: for SQL migrations if needed
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

### 2. Key Implementation Notes

**Authentication Middleware**
- Use FastAPI's `Depends()` for auth injection
- Create separate dependencies for JWT and API key auth
- Cache API key lookups in Redis (Phase 2)

**Vector Search Optimization**
- Pre-compute project description embeddings on create/update
- Batch embedding generation for bulk operations
- Use MongoDB aggregation pipeline for complex queries

**Error Handling**
- Use FastAPI exception handlers
- Log all errors with request IDs
- Return consistent error format

**Testing Strategy**
- Unit tests for services
- Integration tests for API endpoints
- Mock external APIs (Jira, MongoDB)
- Load testing for vector search

### 3. Security Checklist
- [ ] All passwords hashed with bcrypt (min 12 rounds)
- [ ] JWT secrets stored in environment variables
- [ ] Jira tokens encrypted at rest (AES-256)
- [ ] Rate limiting on all public endpoints
- [ ] Input validation with Pydantic
- [ ] SQL injection prevention (use Motor, not raw queries)
- [ ] CORS configured properly
- [ ] HTTPS enforced in production
- [ ] API keys use cryptographically secure randomness
- [ ] Sensitive data never logged

### 4. Monitoring & Observability
- Structured logging (JSON format)
- Request ID tracking
- Performance metrics (response times)
- Database query performance
- Vector search latency
- External API call tracking (Jira)
- Error rate monitoring
- Cost analytics dashboard

---

## Next Steps

1. Set up MongoDB Atlas cluster with Vector Search enabled
2. Initialize FastAPI project structure (use template above)
3. Implement authentication layer (JWT + API keys)
4. Build core API endpoints (projects, context)
5. Integrate embedding generation (sentence-transformers)
6. Add analytics tracking (token counting)
7. Implement Jira OAuth integration
8. Build MCP server tools
9. Test end-to-end context sharing
10. Deploy to production (Docker + Cloud Run / Railway / Fly.io)
