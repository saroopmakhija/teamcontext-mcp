from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.routers import context, auth, projects
from app.config import settings

app = FastAPI(
    title="TeamContext API",
    description="GitHub-style context sharing for MCP clients",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Event handlers
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(context.router)

@app.get("/")
async def root():
    return {
        "message": "TeamContext API",
        "version": "0.1.0",
        "environment": settings.environment
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
