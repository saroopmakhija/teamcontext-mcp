"""
Comprehensive Test Suite for RAG Chatbot

Tests cover:
1. Code-only queries (constructor parameters, function definitions, class methods)
2. Text-only queries (project plans, documentation, requirements)
3. Mixed code+text queries
4. Hallucination detection and evaluation
5. Context relevance verification
"""

import asyncio
import httpx
from datetime import datetime
from typing import Dict, List, Any
import re

BASE_URL = "http://localhost:8000"

class RAGEvaluator:
    """Evaluates RAG responses for accuracy and hallucination detection"""

    @staticmethod
    def check_hallucination(response: str, sources: List[Dict]) -> Dict[str, Any]:
        """
        Detect potential hallucinations by checking if response content
        is grounded in the provided sources.
        """
        source_texts = " ".join([s["content"] for s in sources])

        # Extract key claims from response (simple heuristic)
        response_lines = [line.strip() for line in response.split('\n') if line.strip()]

        hallucination_score = 0.0
        total_claims = len(response_lines)
        grounded_claims = 0

        for line in response_lines:
            # Skip very short lines or headers
            if len(line) < 10 or line.endswith(':'):
                continue

            # Check if key terms from response appear in sources
            words = set(line.lower().split())
            source_words = set(source_texts.lower().split())

            overlap = len(words.intersection(source_words))
            if overlap > len(words) * 0.3:  # 30% overlap threshold
                grounded_claims += 1

        if total_claims > 0:
            hallucination_score = 1.0 - (grounded_claims / total_claims)

        return {
            "hallucination_score": hallucination_score,
            "grounded_claims": grounded_claims,
            "total_claims": total_claims,
            "status": "PASS" if hallucination_score < 0.3 else "WARNING" if hallucination_score < 0.6 else "FAIL"
        }

    @staticmethod
    def check_context_relevance(query: str, sources: List[Dict], expected_keywords: List[str]) -> Dict[str, Any]:
        """
        Check if retrieved context is relevant to the query.
        """
        source_texts = " ".join([s["content"] for s in sources]).lower()

        found_keywords = []
        missing_keywords = []

        for keyword in expected_keywords:
            if keyword.lower() in source_texts:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)

        relevance_score = len(found_keywords) / len(expected_keywords) if expected_keywords else 0.0

        return {
            "relevance_score": relevance_score,
            "found_keywords": found_keywords,
            "missing_keywords": missing_keywords,
            "status": "PASS" if relevance_score >= 0.8 else "WARNING" if relevance_score >= 0.5 else "FAIL"
        }

    @staticmethod
    def evaluate_response(query: str, response: str, sources: List[Dict], expected_keywords: List[str]) -> Dict[str, Any]:
        """
        Comprehensive evaluation of RAG response.
        """
        hallucination_eval = RAGEvaluator.check_hallucination(response, sources)
        context_eval = RAGEvaluator.check_context_relevance(query, sources, expected_keywords)

        # Overall score
        overall_score = (
            (1.0 - hallucination_eval["hallucination_score"]) * 0.5 +
            context_eval["relevance_score"] * 0.5
        )

        return {
            "overall_score": overall_score,
            "hallucination_eval": hallucination_eval,
            "context_eval": context_eval,
            "status": "PASS" if overall_score >= 0.7 else "WARNING" if overall_score >= 0.5 else "FAIL"
        }


async def setup_test_project(client, headers) -> Dict[str, str]:
    """Create test project and return project_id"""
    project_response = await client.post(
        f"{BASE_URL}/api/v1/projects/",
        headers=headers,
        json={
            "name": "Comprehensive RAG Test Project",
            "description": "Testing code, text, and mixed content retrieval"
        }
    )

    if project_response.status_code != 200:
        raise Exception(f"Failed to create project: {project_response.text}")

    return project_response.json()["id"]


async def test_code_only_queries(client, headers, project_id):
    """Test Suite 1: Code-Only Queries"""
    print("\n" + "=" * 80)
    print("TEST SUITE 1: CODE-ONLY QUERIES")
    print("=" * 80)

    # Store code chunks
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
        self.token_expiry = token_expiry
        self.hash_algorithm = 'HS256'""",
            "metadata": {"type": "code", "language": "python", "class": "UserAuthentication"}
        },
        {
            "content": """def generate_token(self, user_id: str, email: str) -> str:
    \"\"\"
    Generate JWT token for authenticated user.

    Args:
        user_id: Unique user identifier
        email: User's email address

    Returns:
        str: Encoded JWT token
    \"\"\"
    payload = {
        'sub': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(seconds=self.token_expiry)
    }
    return jwt.encode(payload, self.secret_key, algorithm=self.hash_algorithm)""",
            "metadata": {"type": "code", "language": "python", "class": "UserAuthentication", "method": "generate_token"}
        },
        {
            "content": """class DatabaseConnection:
    def __init__(self, host: str, port: int, database: str, username: str, password: str, pool_size: int = 10):
        \"\"\"
        Initialize database connection pool.

        Args:
            host: Database host address
            port: Database port number
            database: Database name
            username: Database username
            password: Database password
            pool_size: Maximum connection pool size (default: 10)
        \"\"\"
        self.host = host
        self.port = port
        self.database = database
        self.credentials = (username, password)
        self.pool_size = pool_size
        self.connection_pool = None""",
            "metadata": {"type": "code", "language": "python", "class": "DatabaseConnection"}
        }
    ]

    print("\n📝 Storing code chunks...")
    chunk_response = await client.post(
        f"{BASE_URL}/api/v1/context/chunk-and-embed",
        headers=headers,
        json={
            "project_id": project_id,
            "chunks": code_chunks,
            "source": "code_repository",
            "tags": ["python", "code", "authentication", "database"]
        }
    )

    if chunk_response.status_code != 200:
        print(f"❌ Failed to store code chunks: {chunk_response.text}")
        return []

    print(f"✅ Stored {len(code_chunks)} code chunks")

    # Test cases for code queries
    test_cases = [
        {
            "name": "Constructor Parameters - UserAuthentication",
            "query": "What are the parameters of the UserAuthentication class constructor?",
            "expected_keywords": ["db_connection", "secret_key", "token_expiry", "3600"],
            "expected_in_response": ["db_connection", "secret_key", "token_expiry"]
        },
        {
            "name": "Constructor Parameters - DatabaseConnection",
            "query": "What parameters does DatabaseConnection __init__ method accept?",
            "expected_keywords": ["host", "port", "database", "username", "password", "pool_size"],
            "expected_in_response": ["host", "port", "database", "username", "password"]
        },
        {
            "name": "Method Signature",
            "query": "What are the arguments for the generate_token method?",
            "expected_keywords": ["user_id", "email", "str"],
            "expected_in_response": ["user_id", "email"]
        },
        {
            "name": "Default Parameter Value",
            "query": "What is the default value of token_expiry in UserAuthentication?",
            "expected_keywords": ["3600", "token_expiry"],
            "expected_in_response": ["3600"]
        }
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'─' * 80}")
        print(f"CODE TEST {i}: {test_case['name']}")
        print(f"{'─' * 80}")
        print(f"🧑 Query: {test_case['query']}")

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

        print(f"\n🤖 AI Response:\n{ai_response}")
        print(f"\n📚 Sources: {len(sources)} chunks retrieved")
        for j, src in enumerate(sources, 1):
            print(f"   {j}. Similarity: {src['similarity_score']:.4f} | Class: {src['metadata'].get('class', 'N/A')}")

        # Evaluate response
        evaluation = RAGEvaluator.evaluate_response(
            test_case['query'],
            ai_response,
            sources,
            test_case['expected_keywords']
        )

        # Check if expected terms are in response
        response_lower = ai_response.lower()
        found_expected = [term for term in test_case['expected_in_response'] if term.lower() in response_lower]
        missing_expected = [term for term in test_case['expected_in_response'] if term.lower() not in response_lower]

        print(f"\n📊 EVALUATION:")
        print(f"   Overall Score: {evaluation['overall_score']:.2%} [{evaluation['status']}]")
        print(f"   Hallucination: {evaluation['hallucination_eval']['hallucination_score']:.2%} [{evaluation['hallucination_eval']['status']}]")
        print(f"   Context Relevance: {evaluation['context_eval']['relevance_score']:.2%} [{evaluation['context_eval']['status']}]")
        print(f"   Expected Terms Found: {len(found_expected)}/{len(test_case['expected_in_response'])}")
        if found_expected:
            print(f"      ✅ Found: {', '.join(found_expected)}")
        if missing_expected:
            print(f"      ❌ Missing: {', '.join(missing_expected)}")

        results.append({
            "test_name": test_case['name'],
            "query": test_case['query'],
            "evaluation": evaluation,
            "found_expected": found_expected,
            "missing_expected": missing_expected
        })

    return results


async def test_text_only_queries(client, headers, project_id):
    """Test Suite 2: Text-Only Queries (Project Plans, Documentation)"""
    print("\n" + "=" * 80)
    print("TEST SUITE 2: TEXT-ONLY QUERIES")
    print("=" * 80)

    # Store text chunks
    text_chunks = [
        {
            "content": """Project Timeline - Q1 2025
Phase 1 (Jan 1-15): Requirements gathering and system design
- Stakeholder interviews: Jan 2-5
- Technical architecture design: Jan 8-12
- Database schema finalization: Jan 13-15

Phase 2 (Jan 16-31): Backend development
- API endpoints implementation: Jan 16-25
- Authentication system: Jan 26-28
- Database integration: Jan 29-31

Phase 3 (Feb 1-28): Frontend development and testing
- UI component development: Feb 1-15
- Integration testing: Feb 16-22
- User acceptance testing: Feb 23-28""",
            "metadata": {"type": "text", "category": "project_plan", "quarter": "Q1_2025"}
        },
        {
            "content": """Team Assignments and Responsibilities

Backend Team:
- Lead: Sarah Chen (sarah@example.com)
- Developers: Mike Johnson, Alex Kumar
- Responsibilities: REST API, database, authentication, deployment
- Estimated hours: 320 hours total

Frontend Team:
- Lead: Emily Rodriguez (emily@example.com)
- Developers: James Park, Lisa Wang
- Responsibilities: React components, state management, UI/UX
- Estimated hours: 280 hours total

DevOps:
- Lead: Tom Anderson (tom@example.com)
- Responsibilities: CI/CD pipeline, AWS infrastructure, monitoring
- Estimated hours: 160 hours total""",
            "metadata": {"type": "text", "category": "team_structure"}
        },
        {
            "content": """Budget Breakdown - Total: $150,000

Development Costs: $95,000
- Backend development: $40,000
- Frontend development: $35,000
- DevOps and infrastructure: $20,000

Third-Party Services: $30,000
- AWS hosting: $12,000/year
- MongoDB Atlas: $8,000/year
- Authentication service (Auth0): $6,000/year
- Monitoring tools (DataDog): $4,000/year

Contingency Fund: $25,000
- Reserved for unexpected costs and scope changes""",
            "metadata": {"type": "text", "category": "budget"}
        },
        {
            "content": """System Requirements

Functional Requirements:
1. User authentication with email/password and OAuth
2. Role-based access control (Admin, User, Guest)
3. Real-time notifications via WebSocket
4. File upload with maximum size of 50MB
5. Export data to PDF and CSV formats
6. Search functionality with filters

Non-Functional Requirements:
1. API response time < 200ms for 95% of requests
2. Support 10,000 concurrent users
3. 99.9% uptime SLA
4. Data encryption at rest and in transit
5. GDPR compliance for EU users""",
            "metadata": {"type": "text", "category": "requirements"}
        }
    ]

    print("\n📝 Storing text chunks...")
    chunk_response = await client.post(
        f"{BASE_URL}/api/v1/context/chunk-and-embed",
        headers=headers,
        json={
            "project_id": project_id,
            "chunks": text_chunks,
            "source": "project_documentation",
            "tags": ["documentation", "planning", "requirements"]
        }
    )

    if chunk_response.status_code != 200:
        print(f"❌ Failed to store text chunks: {chunk_response.text}")
        return []

    print(f"✅ Stored {len(text_chunks)} text chunks")

    # Test cases for text queries
    test_cases = [
        {
            "name": "Project Timeline - Phase 2",
            "query": "What activities are planned for Phase 2 of the project?",
            "expected_keywords": ["Backend development", "API endpoints", "Authentication", "Database integration", "Jan 16-31"],
            "expected_in_response": ["Backend development", "API endpoints", "Authentication"]
        },
        {
            "name": "Team Lead Contact",
            "query": "Who is the lead of the Backend team and what is their email?",
            "expected_keywords": ["Sarah Chen", "sarah@example.com", "Backend"],
            "expected_in_response": ["Sarah Chen", "sarah@example.com"]
        },
        {
            "name": "Budget Allocation",
            "query": "How much is allocated for AWS hosting in the budget?",
            "expected_keywords": ["AWS", "12,000", "hosting"],
            "expected_in_response": ["12,000", "AWS"]
        },
        {
            "name": "Non-Functional Requirements",
            "query": "What is the required API response time and uptime SLA?",
            "expected_keywords": ["200ms", "99.9%", "uptime", "response time"],
            "expected_in_response": ["200ms", "99.9%"]
        },
        {
            "name": "Team Resource Allocation",
            "query": "How many total hours are estimated for the Frontend team?",
            "expected_keywords": ["280 hours", "Frontend", "estimated"],
            "expected_in_response": ["280"]
        }
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'─' * 80}")
        print(f"TEXT TEST {i}: {test_case['name']}")
        print(f"{'─' * 80}")
        print(f"🧑 Query: {test_case['query']}")

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

        print(f"\n🤖 AI Response:\n{ai_response}")
        print(f"\n📚 Sources: {len(sources)} chunks retrieved")
        for j, src in enumerate(sources, 1):
            print(f"   {j}. Similarity: {src['similarity_score']:.4f} | Category: {src['metadata'].get('category', 'N/A')}")

        # Evaluate response
        evaluation = RAGEvaluator.evaluate_response(
            test_case['query'],
            ai_response,
            sources,
            test_case['expected_keywords']
        )

        # Check if expected terms are in response
        response_lower = ai_response.lower()
        found_expected = [term for term in test_case['expected_in_response'] if term.lower() in response_lower]
        missing_expected = [term for term in test_case['expected_in_response'] if term.lower() not in response_lower]

        print(f"\n📊 EVALUATION:")
        print(f"   Overall Score: {evaluation['overall_score']:.2%} [{evaluation['status']}]")
        print(f"   Hallucination: {evaluation['hallucination_eval']['hallucination_score']:.2%} [{evaluation['hallucination_eval']['status']}]")
        print(f"   Context Relevance: {evaluation['context_eval']['relevance_score']:.2%} [{evaluation['context_eval']['status']}]")
        print(f"   Expected Terms Found: {len(found_expected)}/{len(test_case['expected_in_response'])}")
        if found_expected:
            print(f"      ✅ Found: {', '.join(found_expected)}")
        if missing_expected:
            print(f"      ❌ Missing: {', '.join(missing_expected)}")

        results.append({
            "test_name": test_case['name'],
            "query": test_case['query'],
            "evaluation": evaluation,
            "found_expected": found_expected,
            "missing_expected": missing_expected
        })

    return results


async def test_mixed_code_text_queries(client, headers, project_id):
    """Test Suite 3: Mixed Code + Text Queries"""
    print("\n" + "=" * 80)
    print("TEST SUITE 3: MIXED CODE + TEXT QUERIES")
    print("=" * 80)

    # Store mixed chunks
    mixed_chunks = [
        {
            "content": """# API Endpoint Documentation

## POST /api/auth/login

Authenticates a user and returns a JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "expires_in": 3600
}
```

**Error Codes:**
- 401: Invalid credentials
- 429: Too many login attempts""",
            "metadata": {"type": "mixed", "category": "api_documentation", "endpoint": "/api/auth/login"}
        },
        {
            "content": """## Implementation Guide: Rate Limiting

To prevent brute force attacks, implement rate limiting on authentication endpoints:

```python
from fastapi import HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(credentials: LoginRequest):
    # Authentication logic here
    pass
```

Configuration:
- Limit: 5 requests per minute per IP
- Lockout duration: 15 minutes after 5 failed attempts
- Whitelist: Allow unlimited requests from 10.0.0.0/8 (internal network)""",
            "metadata": {"type": "mixed", "category": "implementation_guide", "topic": "rate_limiting"}
        }
    ]

    print("\n📝 Storing mixed chunks...")
    chunk_response = await client.post(
        f"{BASE_URL}/api/v1/context/chunk-and-embed",
        headers=headers,
        json={
            "project_id": project_id,
            "chunks": mixed_chunks,
            "source": "technical_documentation",
            "tags": ["api", "code", "documentation", "mixed"]
        }
    )

    if chunk_response.status_code != 200:
        print(f"❌ Failed to store mixed chunks: {chunk_response.text}")
        return []

    print(f"✅ Stored {len(mixed_chunks)} mixed chunks")

    # Test cases for mixed queries
    test_cases = [
        {
            "name": "API Endpoint Details",
            "query": "What are the error codes for the /api/auth/login endpoint?",
            "expected_keywords": ["401", "429", "Invalid credentials", "Too many login attempts"],
            "expected_in_response": ["401", "429"]
        },
        {
            "name": "Rate Limiting Configuration",
            "query": "What is the rate limit configuration for login attempts?",
            "expected_keywords": ["5", "minute", "15 minutes", "lockout"],
            "expected_in_response": ["5", "minute"]
        },
        {
            "name": "Code Implementation Detail",
            "query": "What decorator is used for rate limiting in the code?",
            "expected_keywords": ["@limiter.limit", "5/minute", "slowapi"],
            "expected_in_response": ["limiter", "limit"]
        }
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'─' * 80}")
        print(f"MIXED TEST {i}: {test_case['name']}")
        print(f"{'─' * 80}")
        print(f"🧑 Query: {test_case['query']}")

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

        print(f"\n🤖 AI Response:\n{ai_response}")
        print(f"\n📚 Sources: {len(sources)} chunks retrieved")

        # Evaluate response
        evaluation = RAGEvaluator.evaluate_response(
            test_case['query'],
            ai_response,
            sources,
            test_case['expected_keywords']
        )

        # Check if expected terms are in response
        response_lower = ai_response.lower()
        found_expected = [term for term in test_case['expected_in_response'] if term.lower() in response_lower]
        missing_expected = [term for term in test_case['expected_in_response'] if term.lower() not in response_lower]

        print(f"\n📊 EVALUATION:")
        print(f"   Overall Score: {evaluation['overall_score']:.2%} [{evaluation['status']}]")
        print(f"   Hallucination: {evaluation['hallucination_eval']['hallucination_score']:.2%} [{evaluation['hallucination_eval']['status']}]")
        print(f"   Context Relevance: {evaluation['context_eval']['relevance_score']:.2%} [{evaluation['context_eval']['status']}]")
        print(f"   Expected Terms Found: {len(found_expected)}/{len(test_case['expected_in_response'])}")
        if found_expected:
            print(f"      ✅ Found: {', '.join(found_expected)}")
        if missing_expected:
            print(f"      ❌ Missing: {', '.join(missing_expected)}")

        results.append({
            "test_name": test_case['name'],
            "query": test_case['query'],
            "evaluation": evaluation,
            "found_expected": found_expected,
            "missing_expected": missing_expected
        })

    return results


def generate_final_report(code_results, text_results, mixed_results):
    """Generate comprehensive evaluation report"""
    all_results = code_results + text_results + mixed_results

    print("\n" + "=" * 80)
    print("FINAL EVALUATION REPORT")
    print("=" * 80)

    total_tests = len(all_results)
    passed = sum(1 for r in all_results if r['evaluation']['status'] == 'PASS')
    warnings = sum(1 for r in all_results if r['evaluation']['status'] == 'WARNING')
    failed = sum(1 for r in all_results if r['evaluation']['status'] == 'FAIL')

    avg_overall = sum(r['evaluation']['overall_score'] for r in all_results) / total_tests if total_tests > 0 else 0
    avg_hallucination = sum(r['evaluation']['hallucination_eval']['hallucination_score'] for r in all_results) / total_tests if total_tests > 0 else 0
    avg_relevance = sum(r['evaluation']['context_eval']['relevance_score'] for r in all_results) / total_tests if total_tests > 0 else 0

    print(f"\n📊 OVERALL STATISTICS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {passed} ({passed/total_tests*100:.1f}%)")
    print(f"   ⚠️  Warnings: {warnings} ({warnings/total_tests*100:.1f}%)")
    print(f"   ❌ Failed: {failed} ({failed/total_tests*100:.1f}%)")

    print(f"\n📈 AVERAGE SCORES:")
    print(f"   Overall Quality: {avg_overall:.2%}")
    print(f"   Hallucination Rate: {avg_hallucination:.2%} (lower is better)")
    print(f"   Context Relevance: {avg_relevance:.2%}")

    print(f"\n📋 DETAILED RESULTS:")

    for category, results in [("CODE", code_results), ("TEXT", text_results), ("MIXED", mixed_results)]:
        if not results:
            continue

        print(f"\n  {category} QUERIES:")
        for result in results:
            status_icon = "✅" if result['evaluation']['status'] == 'PASS' else "⚠️" if result['evaluation']['status'] == 'WARNING' else "❌"
            print(f"    {status_icon} {result['test_name']}")
            print(f"       Score: {result['evaluation']['overall_score']:.2%}")
            print(f"       Expected terms found: {len(result['found_expected'])}/{len(result['found_expected']) + len(result['missing_expected'])}")
            if result['missing_expected']:
                print(f"       Missing: {', '.join(result['missing_expected'])}")

    print(f"\n{'=' * 80}")

    if avg_overall >= 0.7 and avg_hallucination < 0.3:
        print("✅ RAG SYSTEM PASSED COMPREHENSIVE EVALUATION")
    elif avg_overall >= 0.5:
        print("⚠️  RAG SYSTEM NEEDS IMPROVEMENT")
    else:
        print("❌ RAG SYSTEM FAILED EVALUATION")

    print(f"{'=' * 80}\n")


async def run_comprehensive_tests():
    """Main test runner"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("=" * 80)
        print("COMPREHENSIVE RAG EVALUATION SUITE")
        print("=" * 80)

        # Setup: Create user and login
        print("\n📝 Setting up test environment...")
        test_email = f"comprehensive_test_{datetime.now().timestamp()}@test.com"
        test_password = "testpass123"

        # Register
        register_response = await client.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={"email": test_email, "password": test_password, "name": "Comprehensive Test User"}
        )

        if register_response.status_code != 200:
            print(f"❌ Registration failed: {register_response.text}")
            return

        # Login
        login_response = await client.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": test_email, "password": test_password}
        )

        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return

        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # Create project
        project_id = await setup_test_project(client, headers)
        print(f"✅ Test project created: {project_id}")

        # Run test suites
        code_results = await test_code_only_queries(client, headers, project_id)
        text_results = await test_text_only_queries(client, headers, project_id)
        mixed_results = await test_mixed_code_text_queries(client, headers, project_id)

        # Generate final report
        generate_final_report(code_results, text_results, mixed_results)


if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests())
