"""
ULTRA-COMPREHENSIVE RAG TEST SUITE

Tests cover:
1. Precision & Accuracy (exact numbers, dates, emails)
2. Code Edge Cases (similar names, inheritance, generics)
3. Multi-Hop Reasoning (combining multiple sources)
4. Negation & Exclusion queries
5. Comparison & Temporal queries
6. Hallucination Detection (non-existent info)
7. Ambiguous Query Handling
8. Stress Tests (complex scenarios)
"""

import asyncio
import httpx
from datetime import datetime
from typing import Dict, List, Any
import re

BASE_URL = "http://localhost:8000"

class UltraEvaluator:
    """Advanced evaluation metrics for RAG responses"""

    @staticmethod
    def check_exact_match(response: str, expected_values: List[str]) -> Dict[str, Any]:
        """Check for exact matches (case-insensitive)"""
        response_lower = response.lower()
        found = []
        missing = []

        for value in expected_values:
            if value.lower() in response_lower:
                found.append(value)
            else:
                missing.append(value)

        return {
            "found": found,
            "missing": missing,
            "accuracy": len(found) / len(expected_values) * 100 if expected_values else 0
        }

    @staticmethod
    def check_numerical_precision(response: str, expected_numbers: List[str]) -> Dict[str, Any]:
        """Check if specific numbers appear in response (no approximation)"""
        # Extract all numbers from response
        numbers_in_response = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?\b', response)

        found = []
        missing = []

        for num in expected_numbers:
            # Normalize numbers (remove commas)
            normalized_num = num.replace(',', '')
            if any(n.replace(',', '') == normalized_num for n in numbers_in_response):
                found.append(num)
            else:
                missing.append(num)

        return {
            "found": found,
            "missing": missing,
            "precision_score": len(found) / len(expected_numbers) * 100 if expected_numbers else 0
        }

    @staticmethod
    def detect_hallucination_indicators(response: str, sources: List[Dict]) -> Dict[str, Any]:
        """Detect phrases that might indicate hallucination"""

        # Phrases that indicate the model is guessing or uncertain
        uncertain_phrases = [
            "i don't have",
            "not found in",
            "no information",
            "cannot find",
            "doesn't appear",
            "not mentioned",
            "not specified",
            "not available"
        ]

        # Phrases that indicate it's making things up
        hallucination_phrases = [
            "typically",
            "usually",
            "generally",
            "often",
            "might be",
            "could be",
            "possibly",
            "probably",
            "i think",
            "i believe"
        ]

        response_lower = response.lower()

        found_uncertain = [p for p in uncertain_phrases if p in response_lower]
        found_hallucination = [p for p in hallucination_phrases if p in response_lower]

        # Check if response cites sources
        has_citations = any(f"context {i}" in response_lower for i in range(1, 6))

        return {
            "uncertain_phrases": found_uncertain,
            "hallucination_phrases": found_hallucination,
            "has_citations": has_citations,
            "hallucination_risk": "HIGH" if found_hallucination else "LOW" if found_uncertain else "NONE"
        }


async def store_ultra_comprehensive_data(client, headers, project_id):
    """Store comprehensive test data"""

    # Code chunks with edge cases
    code_chunks = [
        {
            "content": """class UserAuthentication:
    \"\"\"Main authentication handler\"\"\"
    def __init__(self, db_connection, secret_key, token_expiry=3600, algorithm='HS256'):
        self.db = db_connection
        self.secret_key = secret_key
        self.token_expiry = token_expiry
        self.algorithm = algorithm

    async def authenticate(self, email: str, password: str) -> dict:
        \"\"\"Authenticate user with email and password\"\"\"
        user = await self.db.users.find_one({"email": email})
        if not user or not verify_password(password, user['hashed_password']):
            raise AuthenticationError("Invalid credentials")
        return self.generate_token(user['id'])""",
            "metadata": {"type": "code", "class": "UserAuthentication", "version": "2.1.0"}
        },
        {
            "content": """class UserAuthenticationService(UserAuthentication):
    \"\"\"Extended authentication service with OAuth support\"\"\"
    def __init__(self, db_connection, secret_key, oauth_providers=None):
        super().__init__(db_connection, secret_key)
        self.oauth_providers = oauth_providers or ['google', 'github']

    async def oauth_authenticate(self, provider: str, token: str) -> dict:
        \"\"\"Authenticate via OAuth provider\"\"\"
        if provider not in self.oauth_providers:
            raise ValueError(f"Unsupported provider: {provider}")
        # OAuth logic here
        return await self._verify_oauth_token(provider, token)""",
            "metadata": {"type": "code", "class": "UserAuthenticationService", "version": "2.1.0"}
        },
        {
            "content": """class DatabaseConnection:
    \"\"\"MongoDB connection handler\"\"\"
    def __init__(self, host='localhost', port=27017, database='mydb',
                 username=None, password=None, pool_size=10, timeout=5000):
        self.host = host
        self.port = port
        self.database = database
        self.pool_size = pool_size
        self.timeout = timeout
        self.connection_string = f"mongodb://{host}:{port}/{database}"

    def get_max_pool_size(self) -> int:
        return self.pool_size""",
            "metadata": {"type": "code", "class": "DatabaseConnection", "version": "1.5.3"}
        }
    ]

    # Text chunks with precise data
    text_chunks = [
        {
            "content": """Project Timeline - Complete Schedule

Phase 1 (Jan 1-15, 2025): Planning & Design
- Stakeholder interviews: Jan 2-5 (4 days)
- System architecture design: Jan 8-12 (5 days)
- Database schema: Jan 13-15 (3 days)
- Total: 12 working days

Phase 2 (Jan 16-31, 2025): Backend Development
- API endpoints: Jan 16-25 (10 days)
- Authentication system: Jan 26-28 (3 days)
- Database integration: Jan 29-31 (3 days)
- Total: 16 working days

Phase 3 (Feb 1-28, 2025): Frontend & Testing
- UI components: Feb 1-15 (15 days)
- Integration testing: Feb 16-22 (7 days)
- UAT: Feb 23-28 (6 days)
- Total: 28 working days""",
            "metadata": {"type": "text", "category": "timeline", "version": "final"}
        },
        {
            "content": """Team Structure & Contact Information

Backend Team (3 members):
- Lead: Sarah Chen (sarah.chen@company.com, ext: 1234)
- Senior Dev: Mike Johnson (mike.j@company.com, ext: 1235)
- Junior Dev: Alex Kumar (alex.kumar@company.com, ext: 1236)
- Estimated hours: 320 total (Sarah: 120, Mike: 120, Alex: 80)
- Budget allocation: $48,000

Frontend Team (3 members):
- Lead: Emily Rodriguez (emily.r@company.com, ext: 2234)
- Senior Dev: James Park (james.park@company.com, ext: 2235)
- Junior Dev: Lisa Wang (lisa.wang@company.com, ext: 2236)
- Estimated hours: 280 total (Emily: 100, James: 100, Lisa: 80)
- Budget allocation: $42,000

DevOps Team (1 member):
- Lead: Tom Anderson (tom.anderson@company.com, ext: 3234)
- Estimated hours: 160 total
- Budget allocation: $28,000""",
            "metadata": {"type": "text", "category": "team", "version": "final"}
        },
        {
            "content": """Detailed Budget Breakdown - Total: $187,500

Development Costs: $118,000
- Backend development: $48,000 (25.6% of total)
- Frontend development: $42,000 (22.4% of total)
- DevOps: $28,000 (14.9% of total)

Third-Party Services (Annual): $43,500
- AWS hosting: $18,000/year (EC2, S3, RDS)
- MongoDB Atlas: $12,000/year (M30 cluster)
- Auth0: $8,500/year (Enterprise plan)
- DataDog monitoring: $5,000/year

Tools & Licenses: $14,000
- JetBrains licenses: $3,000
- GitHub Enterprise: $5,000
- Figma Enterprise: $6,000

Contingency: $12,000 (6.4% of total)""",
            "metadata": {"type": "text", "category": "budget", "version": "final"}
        },
        {
            "content": """Technical Requirements Specification v2.3

Functional Requirements:
FR1: User authentication with email/password (required)
FR2: OAuth 2.0 integration (Google, GitHub) (required)
FR3: Role-based access control: Admin, User, Guest (required)
FR4: Real-time notifications via WebSocket (required)
FR5: File upload: max 100MB, formats: PDF, DOCX, PNG, JPG (required)
FR6: Data export to PDF and CSV (optional)
FR7: Advanced search with filters and facets (required)
FR8: Audit logging for all CRUD operations (required)

Non-Functional Requirements:
NFR1: API response time < 150ms for 95th percentile
NFR2: Support 15,000 concurrent users
NFR3: 99.95% uptime SLA
NFR4: Data encryption: AES-256 at rest, TLS 1.3 in transit
NFR5: GDPR, CCPA, SOC 2 compliance
NFR6: Automated backups every 6 hours
NFR7: RPO: 1 hour, RTO: 4 hours""",
            "metadata": {"type": "text", "category": "requirements", "version": "2.3"}
        }
    ]

    # Mixed technical documentation
    mixed_chunks = [
        {
            "content": """Authentication Flow Documentation

Step 1: Login Request
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "securePassword123"
}

Step 2: Server validates credentials using UserAuthentication.authenticate()
- Checks email exists in database
- Verifies password hash using bcrypt
- Validates account is active and not locked

Step 3: Success Response (200 OK)
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "expires_in": 3600,
  "token_type": "Bearer"
}

Error Responses:
- 401: Invalid credentials (wrong email or password)
- 423: Account locked (too many failed attempts)
- 429: Rate limit exceeded (max 5 attempts per minute)
- 503: Service unavailable (database down)

Rate Limiting: 5 requests/minute per IP
Lockout: 15 minutes after 5 failed attempts
Session timeout: 3600 seconds (1 hour)""",
            "metadata": {"type": "mixed", "category": "api_docs", "endpoint": "/api/v1/auth/login"}
        }
    ]

    print("\n📝 Storing ultra-comprehensive test data...")

    # Store code chunks
    await client.post(
        f"{BASE_URL}/api/v1/context/chunk-and-embed",
        headers=headers,
        json={
            "project_id": project_id,
            "chunks": code_chunks,
            "source": "codebase",
            "tags": ["python", "authentication", "database", "code"]
        }
    )
    await asyncio.sleep(7)

    # Store text chunks
    await client.post(
        f"{BASE_URL}/api/v1/context/chunk-and-embed",
        headers=headers,
        json={
            "project_id": project_id,
            "chunks": text_chunks,
            "source": "documentation",
            "tags": ["planning", "team", "budget", "requirements"]
        }
    )
    await asyncio.sleep(7)

    # Store mixed chunks
    await client.post(
        f"{BASE_URL}/api/v1/context/chunk-and-embed",
        headers=headers,
        json={
            "project_id": project_id,
            "chunks": mixed_chunks,
            "source": "api_documentation",
            "tags": ["api", "authentication", "technical"]
        }
    )

    print("✅ All test data stored successfully")


async def run_test_case(client, headers, project_id, test_case, test_num):
    """Run a single test case with detailed evaluation"""

    await asyncio.sleep(7)  # Rate limit

    print(f"\n{'=' * 80}")
    print(f"TEST {test_num}: {test_case['category']} - {test_case['name']}")
    print(f"{'=' * 80}")
    print(f"\n🧑 Query: {test_case['query']}")

    response = await client.post(
        f"{BASE_URL}/api/v1/context/chat",
        headers=headers,
        json={
            "project_id": project_id,
            "message": test_case['query'],
            "max_context_chunks": test_case.get('max_chunks', 5),
            "similarity_threshold": test_case.get('threshold', 0.2)
        }
    )

    if response.status_code != 200:
        print(f"❌ Request failed: {response.text}")
        return None

    data = response.json()
    ai_response = data["message"]
    sources = data["sources"]

    print(f"\n🤖 AI RESPONSE:")
    print("─" * 80)
    print(ai_response)
    print("─" * 80)

    print(f"\n📚 SOURCES ({len(sources)} chunks):")
    for i, src in enumerate(sources, 1):
        print(f"   {i}. Sim: {src['similarity_score']:.4f} | {src['metadata'].get('type', 'N/A')} | {src['metadata'].get('class', src['metadata'].get('category', 'N/A'))}")

    # Evaluation
    print(f"\n📊 EVALUATION:")

    # 1. Exact value matching
    if 'expected_exact' in test_case:
        exact_match = UltraEvaluator.check_exact_match(ai_response, test_case['expected_exact'])
        print(f"   ✓ Exact Matches: {exact_match['accuracy']:.1f}%")
        if exact_match['found']:
            print(f"      Found: {', '.join(exact_match['found'])}")
        if exact_match['missing']:
            print(f"      Missing: {', '.join(exact_match['missing'])}")

    # 2. Numerical precision
    if 'expected_numbers' in test_case:
        num_check = UltraEvaluator.check_numerical_precision(ai_response, test_case['expected_numbers'])
        print(f"   ✓ Numerical Precision: {num_check['precision_score']:.1f}%")
        if num_check['found']:
            print(f"      Found: {', '.join(num_check['found'])}")
        if num_check['missing']:
            print(f"      Missing: {', '.join(num_check['missing'])}")

    # 3. Hallucination detection
    hallucination = UltraEvaluator.detect_hallucination_indicators(ai_response, sources)
    print(f"   ✓ Hallucination Risk: {hallucination['hallucination_risk']}")
    if hallucination['uncertain_phrases']:
        print(f"      Uncertain phrases: {', '.join(hallucination['uncertain_phrases'])}")
    if hallucination['hallucination_phrases']:
        print(f"      ⚠️  Guessing phrases: {', '.join(hallucination['hallucination_phrases'])}")
    print(f"      Citations present: {'Yes' if hallucination['has_citations'] else 'No'}")

    # 4. Expected behavior check
    if 'should_contain' in test_case:
        contains_all = all(term.lower() in ai_response.lower() for term in test_case['should_contain'])
        print(f"   ✓ Required terms present: {'Yes' if contains_all else 'No'}")
        if not contains_all:
            missing = [t for t in test_case['should_contain'] if t.lower() not in ai_response.lower()]
            print(f"      Missing: {', '.join(missing)}")

    if 'should_not_contain' in test_case:
        contains_none = not any(term.lower() in ai_response.lower() for term in test_case['should_not_contain'])
        print(f"   ✓ Forbidden terms absent: {'Yes' if contains_none else 'No'}")
        if not contains_none:
            found = [t for t in test_case['should_not_contain'] if t.lower() in ai_response.lower()]
            print(f"      ⚠️  Found forbidden: {', '.join(found)}")

    # Overall assessment
    if 'expected_exact' in test_case:
        accuracy = exact_match['accuracy']
    elif 'expected_numbers' in test_case:
        accuracy = num_check['precision_score']
    else:
        accuracy = 100.0  # For qualitative tests

    status = "✅ PASS" if accuracy >= 80 and hallucination['hallucination_risk'] != 'HIGH' else "⚠️  WARNING" if accuracy >= 50 else "❌ FAIL"
    print(f"\n   {status} - Overall Accuracy: {accuracy:.1f}%")

    return {
        "name": test_case['name'],
        "category": test_case['category'],
        "accuracy": accuracy,
        "hallucination_risk": hallucination['hallucination_risk'],
        "status": status
    }


async def run_ultra_comprehensive_tests():
    """Main test runner with ultra-comprehensive scenarios"""

    async with httpx.AsyncClient(timeout=60.0) as client:
        print("=" * 80)
        print("ULTRA-COMPREHENSIVE RAG EVALUATION SUITE")
        print("=" * 80)

        # Setup
        test_email = f"ultra_test_{datetime.now().timestamp()}@test.com"
        test_password = "testpass123"

        register_response = await client.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={"email": test_email, "password": test_password, "name": "Ultra Test"}
        )

        login_response = await client.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": test_email, "password": test_password}
        )

        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        project_response = await client.post(
            f"{BASE_URL}/api/v1/projects/",
            headers=headers,
            json={
                "name": "Ultra Comprehensive Test",
                "description": "Testing all edge cases and scenarios"
            }
        )
        project_id = project_response.json()["id"]
        print(f"\n✅ Test project created: {project_id}")

        # Store data
        await store_ultra_comprehensive_data(client, headers, project_id)

        # Define ultra-comprehensive test cases
        test_cases = [
            # PRECISION TESTS
            {
                "category": "PRECISION",
                "name": "Exact Number Extraction",
                "query": "What is the exact pool_size default value in DatabaseConnection?",
                "expected_numbers": ["10"],
                "should_contain": ["10"],
                "should_not_contain": ["around 10", "approximately", "about"]
            },
            {
                "category": "PRECISION",
                "name": "Exact Email Extraction",
                "query": "What is Sarah Chen's exact email address?",
                "expected_exact": ["sarah.chen@company.com"],
                "should_not_contain": ["sarah@", "@example.com"]
            },
            {
                "category": "PRECISION",
                "name": "Exact Date Range",
                "query": "What are the exact dates for Phase 2?",
                "expected_exact": ["Jan 16-31", "2025"],
                "should_contain": ["January 16", "January 31"]
            },
            {
                "category": "PRECISION",
                "name": "Exact Percentage",
                "query": "What percentage of the total budget is allocated to backend development?",
                "expected_numbers": ["25.6"],
                "expected_exact": ["25.6%"],
                "should_contain": ["25.6"]
            },

            # CODE EDGE CASES
            {
                "category": "CODE_EDGE",
                "name": "Distinguish Similar Classes",
                "query": "What parameters does UserAuthentication __init__ take, NOT UserAuthenticationService?",
                "expected_exact": ["db_connection", "secret_key", "token_expiry", "algorithm"],
                "should_contain": ["algorithm", "HS256"],
                "should_not_contain": ["oauth_providers"]
            },
            {
                "category": "CODE_EDGE",
                "name": "Inheritance Understanding",
                "query": "What class does UserAuthenticationService inherit from?",
                "expected_exact": ["UserAuthentication"],
                "should_contain": ["UserAuthentication", "inherit"],
                "should_not_contain": ["DatabaseConnection"]
            },
            {
                "category": "CODE_EDGE",
                "name": "Method Return Type",
                "query": "What does the authenticate method in UserAuthentication return?",
                "expected_exact": ["dict"],
                "should_contain": ["dict", "dictionary"]
            },

            # MULTI-HOP REASONING
            {
                "category": "MULTI_HOP",
                "name": "Cross-Reference Team and Phase",
                "query": "Who leads the team responsible for implementing the authentication system in Phase 2?",
                "expected_exact": ["Sarah Chen"],
                "should_contain": ["Sarah", "Backend", "lead"]
            },
            {
                "category": "MULTI_HOP",
                "name": "Budget Calculation",
                "query": "What is the total development cost for Backend and Frontend teams combined?",
                "expected_numbers": ["90,000", "90000"],
                "should_contain": ["90"]
            },

            # NEGATION TESTS
            {
                "category": "NEGATION",
                "name": "Exclusion Query",
                "query": "What activities are NOT part of Phase 1?",
                "should_contain": ["Phase 2", "Phase 3"],
                "should_not_contain": ["Stakeholder interviews", "Jan 2-5"]
            },
            {
                "category": "NEGATION",
                "name": "Class Distinction Negation",
                "query": "What parameters does UserAuthenticationService have that UserAuthentication does NOT have?",
                "expected_exact": ["oauth_providers"],
                "should_contain": ["oauth_providers"],
                "should_not_contain": ["token_expiry", "algorithm"]
            },

            # COMPARISON TESTS
            {
                "category": "COMPARISON",
                "name": "Budget Comparison",
                "query": "Which team has a higher budget allocation: Backend or Frontend?",
                "expected_exact": ["Backend", "$48,000"],
                "should_contain": ["Backend", "48,000", "more", "higher"]
            },
            {
                "category": "COMPARISON",
                "name": "Phase Duration Comparison",
                "query": "Which phase has more working days: Phase 1 or Phase 2?",
                "expected_exact": ["Phase 2", "16"],
                "should_contain": ["Phase 2", "16"]
            },

            # TEMPORAL/SEQUENCE TESTS
            {
                "category": "TEMPORAL",
                "name": "Activity Sequence",
                "query": "What happens after API endpoints implementation is complete in Phase 2?",
                "expected_exact": ["Authentication system", "Jan 26-28"],
                "should_contain": ["authentication", "after", "next"]
            },

            # HALLUCINATION DETECTION
            {
                "category": "HALLUCINATION",
                "name": "Non-Existent Phase",
                "query": "What activities are planned for Phase 4?",
                "should_contain": ["no", "not", "don't have", "cannot find"],
                "should_not_contain": ["Phase 4", "activities in phase 4"]
            },
            {
                "category": "HALLUCINATION",
                "name": "Non-Existent Team Member",
                "query": "What is John Smith's role in the project?",
                "should_contain": ["no", "not found", "don't have", "not mentioned"],
                "should_not_contain": ["John Smith is"]
            },
            {
                "category": "HALLUCINATION",
                "name": "Non-Existent Budget Item",
                "query": "How much is allocated for Kubernetes hosting?",
                "should_contain": ["no", "not", "don't have", "not mentioned"],
                "should_not_contain": ["Kubernetes", "$"]
            },

            # AMBIGUOUS QUERY HANDLING
            {
                "category": "AMBIGUOUS",
                "name": "Multiple Interpretations",
                "query": "Tell me about authentication",
                "should_contain": ["authentication"],
                "max_chunks": 5
            },

            # STRESS TESTS
            {
                "category": "STRESS",
                "name": "Complex Requirement Query",
                "query": "What are all the non-functional requirements related to performance and availability?",
                "expected_exact": ["150ms", "15,000", "99.95%"],
                "should_contain": ["response time", "concurrent users", "uptime"]
            }
        ]

        # Run all tests
        results = []
        for i, test_case in enumerate(test_cases, 1):
            result = await run_test_case(client, headers, project_id, test_case, i)
            if result:
                results.append(result)

        # Final report
        print("\n" + "=" * 80)
        print("ULTRA-COMPREHENSIVE FINAL REPORT")
        print("=" * 80)

        # Categorize results
        categories = {}
        for r in results:
            cat = r['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(r)

        # Overall statistics
        total = len(results)
        passed = sum(1 for r in results if '✅' in r['status'])
        warnings = sum(1 for r in results if '⚠️' in r['status'])
        failed = sum(1 for r in results if '❌' in r['status'])

        avg_accuracy = sum(r['accuracy'] for r in results) / total if total > 0 else 0
        high_risk = sum(1 for r in results if r['hallucination_risk'] == 'HIGH')

        print(f"\n📊 OVERALL STATISTICS:")
        print(f"   Total Tests: {total}")
        print(f"   ✅ Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"   ⚠️  Warnings: {warnings} ({warnings/total*100:.1f}%)")
        print(f"   ❌ Failed: {failed} ({failed/total*100:.1f}%)")
        print(f"   Average Accuracy: {avg_accuracy:.1f}%")
        print(f"   High Hallucination Risk: {high_risk}")

        print(f"\n📋 RESULTS BY CATEGORY:")
        for cat, cat_results in categories.items():
            cat_passed = sum(1 for r in cat_results if '✅' in r['status'])
            cat_total = len(cat_results)
            print(f"\n   {cat} ({cat_passed}/{cat_total} passed):")
            for r in cat_results:
                status_icon = "✅" if "✅" in r['status'] else "⚠️" if "⚠️" in r['status'] else "❌"
                print(f"      {status_icon} {r['name']}: {r['accuracy']:.1f}% accuracy")

        # Final verdict
        print(f"\n{'=' * 80}")
        if avg_accuracy >= 85 and high_risk == 0 and failed == 0:
            print("🎉 EXCELLENT - RAG SYSTEM IS PRODUCTION READY")
        elif avg_accuracy >= 70 and high_risk <= 2:
            print("✅ GOOD - RAG SYSTEM PERFORMING WELL WITH MINOR ISSUES")
        elif avg_accuracy >= 50:
            print("⚠️  FAIR - RAG SYSTEM NEEDS IMPROVEMENT")
        else:
            print("❌ POOR - RAG SYSTEM REQUIRES SIGNIFICANT WORK")
        print(f"{'=' * 80}\n")


if __name__ == "__main__":
    asyncio.run(run_ultra_comprehensive_tests())
