from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import pymongo

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.mongodb_uri)
    print(f"✅ Connected to MongoDB: {settings.mongodb_db_name}")

    # Create indexes for better performance and data integrity
    await create_indexes()

async def create_indexes():
    """Create database indexes for performance and uniqueness"""
    database = get_database()

    # Users collection indexes
    await database.users.create_index("email", unique=True)
    await database.users.create_index("hashed_api_key")  # For faster API key lookups

    # Projects collection indexes
    await database.projects.create_index("owner_id")
    await database.projects.create_index("contributors")
    await database.projects.create_index([("name", pymongo.TEXT), ("description", pymongo.TEXT)])

    # Contexts collection indexes
    await database.contexts.create_index("metadata.project_id")
    await database.contexts.create_index("metadata.created_by")
    await database.contexts.create_index("created_at")

    print("✅ Database indexes created")

async def close_mongo_connection():
    db.client.close()
    print("❌ Closed MongoDB connection")

def get_database():
    return db.client[settings.mongodb_db_name]
