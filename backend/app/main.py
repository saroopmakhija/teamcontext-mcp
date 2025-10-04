from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.routers import context, auth, projects
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    await connect_to_mongo()
    try:
        yield
    finally:
        # --- shutdown ---
        await close_mongo_connection()

app = FastAPI(
    title="TeamContext API",
    description="GitHub-style context sharing for MCP clients",
    version="0.1.0",
    lifespan=lifespan,  # 👈 replaces @app.on_event handlers
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(context.router)

@app.get("/")
async def root():
    return {
        "message": "TeamContext API",
        "version": "0.1.0",
        "environment": settings.environment,
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    # Helpful for `python -m app.main` or `uv run app/main.py`
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
