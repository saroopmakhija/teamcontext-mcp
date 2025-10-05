#!/usr/bin/env python3
"""
Database Setup Script for TeamContext MCP

This script creates the necessary MongoDB collections and indexes
for the TeamContext application.

Usage:
    python setup_database.py
"""

import asyncio
import sys
import os
from datetime import datetime
from bson import ObjectId

# Add the backend directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.db.mongodb import connect_to_mongo, close_mongo_connection, db
from app.config import settings

async def setup_database():
    """Set up the MongoDB database with collections and indexes"""
    
    print("🚀 Starting database setup...")
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    try:
        database = db.client[settings.mongodb_db_name]
        
        # Create collections if they don't exist
        collections = ['users', 'projects', 'chunks', 'vectordb', 'analytics']
        
        for collection_name in collections:
            if collection_name not in await database.list_collection_names():
                await database.create_collection(collection_name)
                print(f"✅ Created collection: {collection_name}")
            else:
                print(f"ℹ️  Collection already exists: {collection_name}")
        
        # Create indexes for better performance
        await create_indexes(database)
        
        # Create sample data (optional)
        await create_sample_data(database)
        
        print("🎉 Database setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        raise
    finally:
        await close_mongo_connection()

async def create_indexes(database):
    """Create database indexes for performance and uniqueness"""
    print("📊 Creating database indexes...")
    
    # Users collection indexes
    await database.users.create_index("email", unique=True)
    await database.users.create_index("api_keys")
    await database.users.create_index("projects")
    print("✅ Users indexes created")
    
    # Projects collection indexes
    await database.projects.create_index("owner_id")
    await database.projects.create_index("contributors")
    await database.projects.create_index("chunks")
    await database.projects.create_index([("name", "text"), ("description", "text")])
    print("✅ Projects indexes created")
    
    # Chunks collection indexes
    await database.chunks.create_index("project_id")
    await database.chunks.create_index("user_id")
    await database.chunks.create_index("created_at")
    await database.chunks.create_index([("content", "text")])
    print("✅ Chunks indexes created")

async def create_sample_data(database):
    """Create sample data for testing"""
    print("📝 Creating sample data...")
    
    # Check if sample user already exists
    existing_user = await database.users.find_one({"email": "john@example.com"})
    if existing_user:
        print("ℹ️  Sample user already exists, skipping sample data creation")
        return
    
    # Sample user
    sample_user = {
        "_id": ObjectId(),
        "name": "John Doe",
        "email": "john@example.com",
        "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J5k8V7.7a",  # "password123"
        "api_keys": [
            {
                "id": str(ObjectId()),
                "name": "Default Key",
                "key": "sample_api_key_12345",
                "created_at": datetime.now(datetime.UTC)
            }
        ],
        "projects": [],
        "created_at": datetime.now(datetime.UTC),
        "updated_at": datetime.now(datetime.UTC)
    }
    
    # Sample project
    sample_project = {
        "_id": ObjectId(),
        "name": "My First Project",
        "description": "A sample project to get started",
        "chunks": [],
        "owner_id": str(sample_user["_id"]),
        "owner_name": sample_user["name"],
        "contributors": [str(sample_user["_id"])],
        "created_at": datetime.now(datetime.UTC),
        "updated_at": datetime.now(datetime.UTC)
    }
    
    # Sample chunk
    sample_chunk = {
        "_id": ObjectId(),
        "chunk_id": str(ObjectId()),
        "content": "This is a sample chunk of content for testing the database setup.",
        "project_id": str(sample_project["_id"]),
        "user_id": str(sample_user["_id"]),
        "metadata": {
            "source": "setup_script",
            "tags": ["sample", "test"],
            "word_count": 15
        },
        "created_at": datetime.now(datetime.UTC),
        "updated_at": datetime.now(datetime.UTC)
    }
    
    # Insert sample data
    await database.users.insert_one(sample_user)
    await database.projects.insert_one(sample_project)
    await database.chunks.insert_one(sample_chunk)
    
    # Update project with chunk reference
    await database.projects.update_one(
        {"_id": sample_project["_id"]},
        {"$push": {"chunks": sample_chunk["chunk_id"]}}
    )
    
    # Update user with project reference
    await database.users.update_one(
        {"_id": sample_user["_id"]},
        {"$push": {"projects": str(sample_project["_id"])}}
    )
    
    print("✅ Sample data created")
    print(f"   - User: {sample_user['email']} (ID: {sample_user['_id']})")
    print(f"   - Project: {sample_project['name']} (ID: {sample_project['_id']})")
    print(f"   - Chunk: {sample_chunk['chunk_id']}")

if __name__ == "__main__":
    asyncio.run(setup_database())
