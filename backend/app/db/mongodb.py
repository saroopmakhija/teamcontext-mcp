from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.mongodb_uri)
    print(f"✅ Connected to MongoDB: {settings.mongodb_db_name}")

async def close_mongo_connection():
    db.client.close()
    print("❌ Closed MongoDB connection")

def get_database():
    return db.client[settings.mongodb_db_name]
