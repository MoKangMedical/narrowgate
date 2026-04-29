"""
窄门 (NarrowGate) — API Endpoint Tests

Tests for the FastAPI REST endpoints.
Uses httpx AsyncClient with ASGITransport for async testing.
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

# Ensure src and src/api are on the path (main.py uses `from expert_routes import router`)
_src = str(Path(__file__).parent.parent / "src")
_src_api = str(Path(__file__).parent.parent / "src" / "api")
if _src not in sys.path:
    sys.path.insert(0, _src)
if _src_api not in sys.path:
    sys.path.insert(0, _src_api)


# ============================================================
# Module-level setup — mock MIMO before importing the app
# ============================================================

@pytest.fixture(autouse=True)
def mock_env():
    """Set required environment variables for tests."""
    with patch.dict(os.environ, {"MIMO_API_KEY": "test-key"}):
        yield


@pytest.fixture
def app():
    """Import and return the FastAPI app (with MIMO mocked)."""
    with patch("core.mimo_client.MIMOClient") as MockMIMO:
        mock_instance = MockMIMO.return_value
        mock_instance.chat = AsyncMock(return_value="Test AI response")
        mock_instance.master_converse = AsyncMock(return_value="Master test response")
        mock_instance.soul_audit_question = AsyncMock(return_value="Test follow-up question")

        # Clear any cached modules so we get fresh imports with correct paths
        modules_to_remove = [
            k for k in list(sys.modules)
            if k.startswith("api.") or k.startswith("core.")
        ]
        for mod in modules_to_remove:
            del sys.modules[mod]

        from api.main import app as fastapi_app
        yield fastapi_app


@pytest.fixture
async def client(app):
    """Provide an async test client."""
    from httpx import AsyncClient, ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ============================================================
# Health & Index
# ============================================================

class TestHealthEndpoints:
    """Tests for health and root endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """GET /health should return ok status."""
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "narrowgate"

    @pytest.mark.asyncio
    async def test_index_returns_html(self, client):
        """GET / should return HTML content."""
        resp = await client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("content-type", "")


# ============================================================
# User API
# ============================================================

class TestUserAPI:
    """Tests for user endpoints."""

    @pytest.mark.asyncio
    async def test_register_user(self, client):
        """POST /api/user/register should create a user."""
        resp = await client.post(
            "/api/user/register",
            json={"username": "testuser"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        # Username may get suffix if duplicate exists in DB from prior test
        assert "testuser" in data["username"]


# ============================================================
# Soul Audit API
# ============================================================

class TestAuditAPI:
    """Tests for soul audit endpoints."""

    @pytest.mark.asyncio
    async def test_start_audit(self, client):
        """POST /api/audit/start should create an audit session."""
        resp = await client.post(
            "/api/audit/start",
            json={"username": "audit_test_user"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "audit_id" in data
        assert data["status"] == "in_progress"
        assert "question" in data
        assert "dimension" in data

    @pytest.mark.asyncio
    async def test_submit_answer(self, client):
        """POST /api/audit/answer should process a response."""
        # First start an audit
        start_resp = await client.post(
            "/api/audit/start",
            json={"username": "answer_test_user"},
        )
        audit_id = start_resp.json()["audit_id"]

        # Submit an answer
        resp = await client.post(
            "/api/audit/answer",
            json={
                "audit_id": audit_id,
                "answer": "I always avoid conflict",
                "master_id": "socrates",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "evasion_detected" in data

    @pytest.mark.asyncio
    async def test_submit_answer_nonexistent_audit(self, client):
        """Submitting to nonexistent audit should return 404."""
        resp = await client.post(
            "/api/audit/answer",
            json={
                "audit_id": "audit_nonexistent",
                "answer": "test answer",
            },
        )
        assert resp.status_code == 404


# ============================================================
# Masters API
# ============================================================

class TestMastersAPI:
    """Tests for masters endpoints."""

    @pytest.mark.asyncio
    async def test_list_masters(self, client):
        """GET /api/masters should return master list."""
        resp = await client.get("/api/masters")
        assert resp.status_code == 200
        data = resp.json()
        assert "masters" in data
        assert "total" in data
        assert data["total"] >= 3

    @pytest.mark.asyncio
    async def test_get_master_detail(self, client):
        """GET /api/masters/{id} should return master details."""
        resp = await client.get("/api/masters/socrates")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "socrates"
        assert "name" in data
        assert "greeting" in data

    @pytest.mark.asyncio
    async def test_get_master_nonexistent(self, client):
        """GET /api/masters/{id} with bad ID should return 404."""
        resp = await client.get("/api/masters/does_not_exist")
        assert resp.status_code == 404


# ============================================================
# Crossing API
# ============================================================

class TestCrossingAPI:
    """Tests for crossing endpoints."""

    @pytest.mark.asyncio
    async def test_start_crossing(self, client):
        """POST /api/crossing/start should create a crossing."""
        # Register a user first
        reg_resp = await client.post(
            "/api/user/register",
            json={"username": "crossing_user"},
        )
        user_id = reg_resp.json()["id"]

        resp = await client.post(
            "/api/crossing/start",
            json={
                "user_id": user_id,
                "gate_name": "Public Speaking",
                "gate_dimension": "行为",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "crossing_id" in data


# ============================================================
# Witness API
# ============================================================

class TestWitnessAPI:
    """Tests for witness endpoints."""

    @pytest.mark.asyncio
    async def test_add_witness(self, client):
        """POST /api/witness/add should add a witness."""
        resp = await client.post(
            "/api/witness/add",
            json={
                "user_id": "user_test",
                "name": "Test Witness",
                "email": "witness@test.com",
                "relationship": "friend",
            },
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_list_witnesses(self, client):
        """GET /api/witness/list should return witnesses."""
        resp = await client.get(
            "/api/witness/list",
            params={"user_id": "user_test"},
        )
        assert resp.status_code == 200


# ============================================================
# Evolution API
# ============================================================

class TestEvolutionAPI:
    """Tests for evolution endpoints."""

    @pytest.mark.asyncio
    async def test_get_evolution_status(self, client):
        """GET /api/evolution/{user_id} should return evolution data."""
        resp = await client.get("/api/evolution/user_test")
        assert resp.status_code == 200
        data = resp.json()
        assert "level" in data or "current_level" in data


# ============================================================
# OpenAPI / Documentation
# ============================================================

class TestOpenAPI:
    """Tests for API documentation endpoints."""

    @pytest.mark.asyncio
    async def test_openapi_schema(self, client):
        """GET /openapi.json should return valid schema."""
        resp = await client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert "openapi" in schema
        assert "paths" in schema

    @pytest.mark.asyncio
    async def test_docs_page(self, client):
        """GET /docs should return Swagger UI."""
        resp = await client.get("/docs")
        assert resp.status_code == 200
