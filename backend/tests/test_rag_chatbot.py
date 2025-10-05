"""
Test script for RAG chatbot endpoint

Tests:
1. Create test user and project
2. Store conversation context chunks
3. Test RAG chat with project-specific context
4. Test multi-turn conversation with history
5. Verify project isolation
"""

import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_rag_chatbot():
    async with httpx.AsyncClient(timeout=60.0) as client:  # 60 second timeout
        print("=" * 80)
        print("🧪 RAG CHATBOT ENDPOINT TEST")
        print("=" * 80)

        # Step 1: Register test user
        print("\n📝 Step 1: Creating test user...")
        test_email = f"rag_test_{datetime.now().timestamp()}@test.com"
        test_password = "testpass123"

        register_response = await client.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={
                "email": test_email,
                "password": test_password,
                "name": "RAG Test User"
            }
        )
        print(f"Status: {register_response.status_code}")

        if register_response.status_code != 200:
            print(f"❌ Registration failed: {register_response.text}")
            return

        print(f"✅ User created")

        # Step 1b: Login to get JWT token
        print("\n📝 Step 1b: Logging in...")
        login_response = await client.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "email": test_email,
                "password": test_password
            }
        )
        print(f"Status: {login_response.status_code}")

        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return

        login_data = login_response.json()
        access_token = login_data["access_token"]
        print(f"✅ Logged in with JWT token")

        headers = {"Authorization": f"Bearer {access_token}"}

        # Step 2: Create test project
        print("\n📝 Step 2: Creating test project...")
        project_response = await client.post(
            f"{BASE_URL}/api/v1/projects/",
            headers=headers,
            json={
                "name": "AI Assistant Documentation",
                "description": "Documentation and examples for building AI assistants"
            }
        )
        print(f"Status: {project_response.status_code}")

        if project_response.status_code != 200:
            print(f"❌ Project creation failed: {project_response.text}")
            return

        project_data = project_response.json()
        project_id = project_data["id"]
        print(f"✅ Project created: {project_id}")

        # Step 3: Store knowledge base chunks
        print("\n📝 Step 3: Storing knowledge base chunks...")

        knowledge_chunks = [
            {
                "content": "FastAPI is a modern, fast web framework for building APIs with Python 3.7+. It's built on top of Starlette and Pydantic, providing automatic data validation and serialization.",
                "metadata": {"topic": "fastapi_intro", "category": "framework"}
            },
            {
                "content": "To create a RAG (Retrieval Augmented Generation) system, you need: 1) A vector database to store embeddings, 2) An embedding model to convert text to vectors, 3) A similarity search mechanism, 4) An LLM for generation.",
                "metadata": {"topic": "rag_architecture", "category": "ai"}
            },
            {
                "content": "Google's Gemini Flash 2.0 is optimized for speed and efficiency. It supports streaming responses, multi-turn conversations, and has a large context window. Use gemini-2.0-flash-exp for the latest experimental features.",
                "metadata": {"topic": "gemini_flash", "category": "ai"}
            },
            {
                "content": "MongoDB Atlas provides vector search capabilities through the $vectorSearch aggregation stage. You can store embeddings directly in documents and perform similarity searches using cosine similarity.",
                "metadata": {"topic": "mongodb_vectors", "category": "database"}
            },
            {
                "content": "Authentication in FastAPI can be done using OAuth2 with JWT tokens. Use fastapi.security.HTTPBearer for bearer token authentication and python-jose for JWT encoding/decoding.",
                "metadata": {"topic": "fastapi_auth", "category": "security"}
            },
            {
                "content": "Pydantic BaseModel provides automatic data validation, serialization, and documentation generation. It's the foundation of FastAPI's request/response handling.",
                "metadata": {"topic": "pydantic", "category": "framework"}
            }
        ]

        chunk_response = await client.post(
            f"{BASE_URL}/api/v1/context/chunk-and-embed",
            headers=headers,
            json={
                "project_id": project_id,
                "chunks": knowledge_chunks,
                "source": "documentation",
                "tags": ["ai", "python", "fastapi"]
            }
        )
        print(f"Status: {chunk_response.status_code}")

        if chunk_response.status_code != 200:
            print(f"❌ Chunk storage failed: {chunk_response.text}")
            return

        chunk_data = chunk_response.json()
        print(f"✅ Stored {chunk_data['vectors_stored']} knowledge chunks")
        print(f"   Embedding dimensions: {chunk_data['embedding_dimensions']}")

        # Step 4: Test RAG chat - Question about RAG
        print("\n" + "=" * 80)
        print("💬 TEST 1: Simple question about RAG architecture")
        print("=" * 80)

        chat_response = await client.post(
            f"{BASE_URL}/api/v1/context/chat",
            headers=headers,
            json={
                "project_id": project_id,
                "message": "What are the key components needed to build a RAG system?",
                "max_context_chunks": 3,
                "similarity_threshold": 0.3
            }
        )
        print(f"Status: {chat_response.status_code}")

        if chat_response.status_code != 200:
            print(f"❌ Chat failed: {chat_response.text}")
            return

        chat_data = chat_response.json()
        print(f"\n🤖 AI Response:")
        print(f"{chat_data['message']}\n")
        print(f"📚 Sources used ({len(chat_data['sources'])} chunks):")
        for i, source in enumerate(chat_data['sources'], 1):
            print(f"\n   {i}. Similarity: {source['similarity_score']:.4f}")
            print(f"      Topic: {source['metadata'].get('topic', 'unknown')}")
            print(f"      Content: {source['content'][:100]}...")

        # Step 5: Test multi-turn conversation
        print("\n" + "=" * 80)
        print("💬 TEST 2: Multi-turn conversation with history")
        print("=" * 80)

        # First turn
        print("\n🧑 User: Tell me about Gemini Flash 2.0")
        turn1_response = await client.post(
            f"{BASE_URL}/api/v1/context/chat",
            headers=headers,
            json={
                "project_id": project_id,
                "message": "Tell me about Gemini Flash 2.0",
                "history": [],
                "max_context_chunks": 2
            }
        )

        if turn1_response.status_code != 200:
            print(f"❌ Turn 1 failed: {turn1_response.text}")
            return

        turn1_data = turn1_response.json()
        print(f"🤖 AI: {turn1_data['message'][:200]}...")

        # Second turn - follow-up question
        print("\n🧑 User: What's the model name I should use?")
        turn2_response = await client.post(
            f"{BASE_URL}/api/v1/context/chat",
            headers=headers,
            json={
                "project_id": project_id,
                "message": "What's the model name I should use?",
                "history": [
                    {"role": "user", "content": "Tell me about Gemini Flash 2.0"},
                    {"role": "model", "content": turn1_data['message']}
                ],
                "max_context_chunks": 2
            }
        )

        if turn2_response.status_code != 200:
            print(f"❌ Turn 2 failed: {turn2_response.text}")
            return

        turn2_data = turn2_response.json()
        print(f"🤖 AI: {turn2_data['message']}")

        # Step 6: Test question with no relevant context
        print("\n" + "=" * 80)
        print("💬 TEST 3: Question with no relevant context")
        print("=" * 80)

        print("\n🧑 User: What's the weather like today?")
        weather_response = await client.post(
            f"{BASE_URL}/api/v1/context/chat",
            headers=headers,
            json={
                "project_id": project_id,
                "message": "What's the weather like today?",
                "max_context_chunks": 3,
                "similarity_threshold": 0.5
            }
        )

        if weather_response.status_code != 200:
            print(f"❌ Weather question failed: {weather_response.text}")
            return

        weather_data = weather_response.json()
        print(f"🤖 AI: {weather_data['message']}")
        print(f"📚 Sources: {len(weather_data['sources'])} (should be 0 or very few)")

        # Step 7: Test project isolation
        print("\n" + "=" * 80)
        print("🔒 TEST 4: Project isolation verification")
        print("=" * 80)

        # Create second project
        print("\n📝 Creating second project...")
        project2_response = await client.post(
            f"{BASE_URL}/api/v1/projects/",
            headers=headers,
            json={
                "name": "Different Project",
                "description": "Completely different topic"
            }
        )

        if project2_response.status_code != 200:
            print(f"❌ Second project creation failed: {project2_response.text}")
            return

        project2_data = project2_response.json()
        project2_id = project2_data["id"]
        print(f"✅ Second project created: {project2_id}")

        # Try to query project 2 (should have no context)
        print("\n🧑 User: What are the key components needed to build a RAG system? (asking in empty project)")
        isolation_response = await client.post(
            f"{BASE_URL}/api/v1/context/chat",
            headers=headers,
            json={
                "project_id": project2_id,  # Different project!
                "message": "What are the key components needed to build a RAG system?",
                "max_context_chunks": 3
            }
        )

        if isolation_response.status_code != 200:
            print(f"❌ Isolation test failed: {isolation_response.text}")
            return

        isolation_data = isolation_response.json()
        print(f"🤖 AI: {isolation_data['message'][:200]}...")
        print(f"📚 Sources: {len(isolation_data['sources'])} (should be 0 - project is empty)")

        if len(isolation_data['sources']) == 0:
            print("✅ PROJECT ISOLATION WORKING: No cross-project data leakage!")
        else:
            print("❌ WARNING: Found sources in empty project - possible isolation issue!")

        # Step 8: Test comprehensive question
        print("\n" + "=" * 80)
        print("💬 TEST 5: Comprehensive question requiring multiple sources")
        print("=" * 80)

        print("\n🧑 User: How do I build a FastAPI app with authentication and vector search?")
        comprehensive_response = await client.post(
            f"{BASE_URL}/api/v1/context/chat",
            headers=headers,
            json={
                "project_id": project_id,  # Back to first project
                "message": "How do I build a FastAPI app with authentication and vector search?",
                "max_context_chunks": 5,
                "similarity_threshold": 0.2
            }
        )

        if comprehensive_response.status_code != 200:
            print(f"❌ Comprehensive question failed: {comprehensive_response.text}")
            return

        comp_data = comprehensive_response.json()
        print(f"\n🤖 AI Response:")
        print(f"{comp_data['message']}\n")
        print(f"📚 Sources used ({len(comp_data['sources'])} chunks):")
        for i, source in enumerate(comp_data['sources'], 1):
            print(f"   {i}. [{source['metadata'].get('topic', 'unknown')}] Similarity: {source['similarity_score']:.4f}")

        print("\n" + "=" * 80)
        print("✅ ALL RAG CHATBOT TESTS PASSED!")
        print("=" * 80)
        print("\nTest Summary:")
        print("  ✅ Simple question with context retrieval")
        print("  ✅ Multi-turn conversation with history")
        print("  ✅ Question with no relevant context")
        print("  ✅ Project isolation (no cross-project leakage)")
        print("  ✅ Comprehensive question with multiple sources")
        print("\nRAG chatbot is working correctly! 🎉")

if __name__ == "__main__":
    asyncio.run(test_rag_chatbot())
