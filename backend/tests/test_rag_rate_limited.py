"""
Comprehensive RAG Test with Rate Limiting
Runs tests with delays to stay under 10 requests/minute
"""

import asyncio
import httpx
from datetime import datetime
from typing import Dict, List, Any

BASE_URL = "http://localhost:8000"

async def test_with_rate_limit():
    """Run comprehensive tests with 7-second delays between requests"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("=" * 80)
        print("COMPREHENSIVE RAG TEST (Rate Limited)")
        print("=" * 80)

        # Setup
        test_email = f"rag_slow_test_{datetime.now().timestamp()}@test.com"
        test_password = "testpass123"

        # Register
        register_response = await client.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={"email": test_email, "password": test_password, "name": "RAG Test"}
        )

        # Login
        login_response = await client.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": test_email, "password": test_password}
        )

        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # Create project
        project_response = await client.post(
            f"{BASE_URL}/api/v1/projects/",
            headers=headers,
            json={
                "name": "RAG Test Project",
                "description": "Testing RAG with rate limits"
            }
        )
        project_id = project_response.json()["id"]
        print(f"\n✅ Project created: {project_id}")

        # Store code chunks
        print("\n📝 Storing code chunks...")
        code_chunks = [
            {
                "content": """class UserAuthentication:
    def __init__(self, db_connection, secret_key, token_expiry=3600):
        \"\"\"
        Initialize authentication system.

        Args:
            db_connection: Database connection object
            secret_key: Secret key for JWT signing (string)
            token_expiry: Token expiration time in seconds (default: 3600)
        \"\"\"
        self.db = db_connection
        self.secret_key = secret_key
        self.token_expiry = token_expiry""",
                "metadata": {"type": "code", "class": "UserAuthentication"}
            }
        ]

        await client.post(
            f"{BASE_URL}/api/v1/context/chunk-and-embed",
            headers=headers,
            json={
                "project_id": project_id,
                "chunks": code_chunks,
                "source": "code",
                "tags": ["python", "auth"]
            }
        )
        print("✅ Code chunks stored")

        await asyncio.sleep(7)  # Rate limit delay

        # Store text chunks
        print("\n📝 Storing text chunks...")
        text_chunks = [
            {
                "content": """Project Timeline - Q1 2025
Phase 2 (Jan 16-31): Backend development
- API endpoints implementation: Jan 16-25
- Authentication system: Jan 26-28
- Database integration: Jan 29-31""",
                "metadata": {"type": "text", "category": "project_plan"}
            },
            {
                "content": """Team Assignments
Backend Team:
- Lead: Sarah Chen (sarah@example.com)
- Developers: Mike Johnson, Alex Kumar
- Estimated hours: 320 hours total""",
                "metadata": {"type": "text", "category": "team"}
            }
        ]

        await client.post(
            f"{BASE_URL}/api/v1/context/chunk-and-embed",
            headers=headers,
            json={
                "project_id": project_id,
                "chunks": text_chunks,
                "source": "docs",
                "tags": ["planning"]
            }
        )
        print("✅ Text chunks stored")

        # Test cases
        test_cases = [
            {
                "name": "CODE TEST: Constructor Parameters",
                "query": "What are the parameters of the UserAuthentication class constructor?",
                "expected_keywords": ["db_connection", "secret_key", "token_expiry", "3600"]
            },
            {
                "name": "TEXT TEST: Team Lead",
                "query": "Who is the lead of the Backend team and what is their email?",
                "expected_keywords": ["Sarah Chen", "sarah@example.com"]
            },
            {
                "name": "TEXT TEST: Phase 2 Activities",
                "query": "What activities are planned for Phase 2?",
                "expected_keywords": ["Backend development", "API endpoints", "Authentication"]
            }
        ]

        results = []

        for i, test_case in enumerate(test_cases, 1):
            await asyncio.sleep(7)  # Rate limit delay

            print(f"\n{'=' * 80}")
            print(f"TEST {i}: {test_case['name']}")
            print(f"{'=' * 80}")
            print(f"\n🧑 Query: {test_case['query']}")

            response = await client.post(
                f"{BASE_URL}/api/v1/context/chat",
                headers=headers,
                json={
                    "project_id": project_id,
                    "message": test_case['query'],
                    "max_context_chunks": 3,
                    "similarity_threshold": 0.2
                }
            )

            if response.status_code != 200:
                print(f"❌ Request failed: {response.text}")
                continue

            data = response.json()
            ai_response = data["message"]
            sources = data["sources"]

            print(f"\n🤖 AI RESPONSE:")
            print("─" * 80)
            print(ai_response)
            print("─" * 80)

            print(f"\n📚 SOURCES ({len(sources)} chunks):")
            for j, src in enumerate(sources, 1):
                print(f"\n   Source {j}:")
                print(f"   Similarity: {src['similarity_score']:.4f}")
                print(f"   Type: {src['metadata'].get('type', 'N/A')}")
                print(f"   Content Preview: {src['content'][:100]}...")

            # Check for expected keywords
            response_lower = ai_response.lower()
            found = [kw for kw in test_case['expected_keywords'] if kw.lower() in response_lower]
            missing = [kw for kw in test_case['expected_keywords'] if kw.lower() not in response_lower]

            print(f"\n📊 EVALUATION:")
            print(f"   Expected Keywords: {len(test_case['expected_keywords'])}")
            print(f"   ✅ Found: {len(found)} - {', '.join(found) if found else 'None'}")
            print(f"   ❌ Missing: {len(missing)} - {', '.join(missing) if missing else 'None'}")

            accuracy = len(found) / len(test_case['expected_keywords']) * 100
            print(f"   Accuracy: {accuracy:.1f}%")

            # Check for hallucination
            source_text = " ".join([s["content"] for s in sources]).lower()
            response_words = set(response_lower.split())
            source_words = set(source_text.split())
            overlap = len(response_words.intersection(source_words))

            grounding_score = overlap / len(response_words) * 100 if len(response_words) > 0 else 0
            print(f"   Grounding Score: {grounding_score:.1f}% (words from sources)")

            results.append({
                "test": test_case['name'],
                "accuracy": accuracy,
                "grounding": grounding_score,
                "found": found,
                "missing": missing
            })

        # Final report
        print("\n" + "=" * 80)
        print("FINAL REPORT")
        print("=" * 80)

        avg_accuracy = sum(r['accuracy'] for r in results) / len(results) if results else 0
        avg_grounding = sum(r['grounding'] for r in results) / len(results) if results else 0

        print(f"\n📈 OVERALL METRICS:")
        print(f"   Tests Completed: {len(results)}")
        print(f"   Average Accuracy: {avg_accuracy:.1f}%")
        print(f"   Average Grounding: {avg_grounding:.1f}%")

        print(f"\n📋 DETAILED RESULTS:")
        for r in results:
            print(f"\n   {r['test']}")
            print(f"      Accuracy: {r['accuracy']:.1f}%")
            print(f"      Grounding: {r['grounding']:.1f}%")
            if r['found']:
                print(f"      Found: {', '.join(r['found'])}")
            if r['missing']:
                print(f"      Missing: {', '.join(r['missing'])}")

        if avg_accuracy >= 80 and avg_grounding >= 30:
            print(f"\n{'=' * 80}")
            print("✅ RAG SYSTEM PERFORMING WELL")
            print(f"{'=' * 80}\n")
        else:
            print(f"\n{'=' * 80}")
            print("⚠️  RAG SYSTEM NEEDS TUNING")
            print(f"{'=' * 80}\n")


if __name__ == "__main__":
    asyncio.run(test_with_rate_limit())
