from pymongo import AsyncMongoClient
from ..config import settings
import pymongo

class Database:
    client: AsyncMongoClient = None

db = Database()

async def connect_to_mongo():
    db.client = AsyncMongoClient(settings.mongodb_uri)
    print(f"✅ Connected to MongoDB: {settings.mongodb_db_name}")

    # Create indexes for better performance and data integrity
    await create_indexes()

async def create_indexes():
    """Create database indexes for performance and uniqueness"""
    database = db.client[settings.mongodb_db_name]

    # Users collection indexes
    await database.users.create_index("email", unique=True)
    await database.users.create_index("api_keys")
    await database.users.create_index("projects")

    # Projects collection indexes
    await database.projects.create_index("owner_id")
    await database.projects.create_index("contributors")
    await database.projects.create_index("chunks")
    await database.projects.create_index([("name", pymongo.TEXT), ("description", pymongo.TEXT)])

    # Chunks collection indexes
    await database.chunks.create_index("project_id")
    await database.chunks.create_index("user_id")
    await database.chunks.create_index("created_at")
    await database.chunks.create_index([("content", pymongo.TEXT)])

    print("✅ Database indexes created")

async def close_mongo_connection():
    if db.client:
        await db.client.close()
        print("❌ Closed MongoDB connection")

def get_database():
    return db.client[settings.mongodb_db_name]
