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

    @pytest.mark.asyncio
    async def test_frontend_assets_are_served(self, client):
        """Frontend asset URLs referenced by index.html should resolve."""
        css_resp = await client.get("/tailwind.css")
        assert css_resp.status_code == 200
        assert "text/css" in css_resp.headers.get("content-type", "")

        manifest_resp = await client.get("/manifest.json")
        assert manifest_resp.status_code == 200
        assert "json" in manifest_resp.headers.get("content-type", "")

        favicon_resp = await client.get("/favicon.svg")
        assert favicon_resp.status_code == 200
        assert "image/svg+xml" in favicon_resp.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_course_static_page_and_public_data_are_served(self, client):
        """Production routes should serve the static course page and public data files."""
        page_resp = await client.get("/course-system.html")
        assert page_resp.status_code == 200
        assert "text/html" in page_resp.headers.get("content-type", "")

        launch_resp = await client.get("/commercial-launch.html")
        assert launch_resp.status_code == 200
        assert "text/html" in launch_resp.headers.get("content-type", "")
        assert "商业落地" in launch_resp.text

        ops_resp = await client.get("/marketing-ops.html")
        assert ops_resp.status_code == 200
        assert "text/html" in ops_resp.headers.get("content-type", "")
        assert "增长执行台" in ops_resp.text
        assert "14天发布作战表" in ops_resp.text

        catalog_resp = await client.get("/data/course_catalog_100.json")
        assert catalog_resp.status_code == 200
        assert "json" in catalog_resp.headers.get("content-type", "")
        assert len(catalog_resp.json()) == 100

        campaign_resp = await client.get("/data/marketing/launch_campaign_30d.json")
        assert campaign_resp.status_code == 200
        assert "json" in campaign_resp.headers.get("content-type", "")
        assert len(campaign_resp.json()["items"]) == 30

        assets_resp = await client.get("/data/marketing/publishing_assets.json")
        assert assets_resp.status_code == 200
        assert "json" in assets_resp.headers.get("content-type", "")
        assert len(assets_resp.json()["items"]) == 30

        checklist_resp = await client.get("/data/marketing/week1_publish_checklist.json")
        assert checklist_resp.status_code == 200
        assert len(checklist_resp.json()["tasks"]) == 14

        calendar_resp = await client.get("/data/marketing/launch_production_calendar.json")
        assert calendar_resp.status_code == 200
        calendar = calendar_resp.json()
        assert len(calendar["calendar"]) == 14
        assert calendar["calendar"][0]["account"].startswith("小红书")
        assert calendar["calendar"][0]["publish_at"] == "2026-06-01T21:30"

        calendar_md_resp = await client.get("/data/marketing/launch_production_calendar.md")
        assert calendar_md_resp.status_code == 200
        assert "窄门14天发布作战表" in calendar_md_resp.text

        calendar_csv_resp = await client.get("/data/marketing/launch_production_calendar.csv")
        assert calendar_csv_resp.status_code == 200
        assert "text/csv" in calendar_csv_resp.headers.get("content-type", "")

        scripts_resp = await client.get("/data/marketing/week1_publish_scripts.md")
        assert scripts_resp.status_code == 200
        assert "窄门首周逐条发布话术" in scripts_resp.text

        storyboard_resp = await client.get("/data/marketing/digital_human_storyboards.json")
        assert storyboard_resp.status_code == 200
        assert len(storyboard_resp.json()["storyboards"]) == 10

        csv_resp = await client.get("/data/marketing/publishing_assets.csv")
        assert csv_resp.status_code == 200
        assert "text/csv" in csv_resp.headers.get("content-type", "")

        audio_resp = await client.get("/data/courses/belief_audit/audio/intro.mp3")
        assert audio_resp.status_code == 200
        assert audio_resp.headers["content-type"].startswith("audio/mpeg")

        db_resp = await client.get("/data/narrowgate.db")
        assert db_resp.status_code == 404


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
# Marketing Lead API
# ============================================================

class TestMarketingLeadAPI:
    """Tests for commercial launch lead capture."""

    @pytest.mark.asyncio
    async def test_create_marketing_lead(self, client):
        """POST /api/marketing/leads should capture a channel lead."""
        resp = await client.post(
            "/api/marketing/leads",
            json={
                "source": "pytest",
                "channel": "xiaohongshu",
                "intent": "institution",
                "name": "测试机构",
                "contact": "test@example.com",
                "organization": "窄门测试机构",
                "note": "希望了解机构合作",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["lead_id"].startswith("lead_")

    @pytest.mark.asyncio
    async def test_create_marketing_lead_requires_contact(self, client):
        """Lead capture should require contact info."""
        resp = await client.post(
            "/api/marketing/leads",
            json={"channel": "douyin", "intent": "trial"},
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_marketing_campaign_api_has_tracking_links(self, client):
        """GET /api/marketing/campaign should expose publish-ready UTM links."""
        resp = await client.get("/api/marketing/campaign")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 30
        first = data["items"][0]
        assert first["status"] == "ready_to_publish"
        assert "utm_source=" in first["landing_url"]
        assert "quality_gate" in first

    @pytest.mark.asyncio
    async def test_marketing_lead_summary_hides_contacts(self, client):
        """Public summary should not expose personal contact fields."""
        await client.post(
            "/api/marketing/leads",
            json={
                "source": "pytest_summary",
                "channel": "digital_human",
                "intent": "trial",
                "contact": "summary@example.com",
            },
        )
        resp = await client.get("/api/marketing/leads/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert "contact" not in str(data)

    @pytest.mark.asyncio
    async def test_marketing_lead_export_requires_admin_token(self, client):
        """Lead detail export should require the configured admin token."""
        resp = await client.get("/api/marketing/leads")
        assert resp.status_code == 403

        with patch.dict(os.environ, {"NARROWGATE_ADMIN_TOKEN": "pytest-admin"}):
            ok_resp = await client.get(
                "/api/marketing/leads",
                headers={"X-Admin-Token": "pytest-admin"},
            )
            assert ok_resp.status_code == 200
            assert "leads" in ok_resp.json()

            csv_resp = await client.get(
                "/api/marketing/leads.csv",
                headers={"X-Admin-Token": "pytest-admin"},
            )
            assert csv_resp.status_code == 200
            assert "text/csv" in csv_resp.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_marketing_post_status_and_metrics_flow(self, client):
        """Operators should be able to save publishing status and metrics."""
        payload = {
            "content_id": "day01_xiaohongshu",
            "day": 1,
            "channel": "xiaohongshu",
            "title": "你不是不自律，你是在逃避一个真问题",
            "status": "published",
            "publish_url": "https://example.com/post/day01",
            "metrics": {
                "views": 1200,
                "likes": 80,
                "comments": 12,
                "favorites": 45,
                "shares": 8,
                "leads": 3,
            },
            "notes": "评论集中在拖延和关系边界。",
        }
        no_token = await client.post("/api/marketing/posts", json=payload)
        assert no_token.status_code == 403

        with patch.dict(os.environ, {"NARROWGATE_ADMIN_TOKEN": "pytest-admin"}):
            resp = await client.post(
                "/api/marketing/posts",
                headers={"X-Admin-Token": "pytest-admin"},
                json=payload,
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True
            assert data["post"]["metrics"]["leads"] == 3

        list_resp = await client.get("/api/marketing/posts")
        assert list_resp.status_code == 200
        assert any(post["content_id"] == "day01_xiaohongshu" for post in list_resp.json()["posts"])

        summary_resp = await client.get("/api/marketing/posts/summary")
        assert summary_resp.status_code == 200
        summary = summary_resp.json()
        assert summary["metrics"]["views"] >= 1200
        assert summary["metrics"]["leads"] >= 3

        report_resp = await client.get("/api/marketing/posts/weekly-report")
        assert report_resp.status_code == 200
        report = report_resp.json()
        assert report["post_count"] >= 1
        assert report["reuse_suggestions"][0]["next_action"]

        markdown_resp = await client.get("/api/marketing/posts/weekly-report.md")
        assert markdown_resp.status_code == 200
        assert "窄门增长周报" in markdown_resp.text


# ============================================================
# Deep Course Library API
# ============================================================

class TestDeepCourseLibraryAPI:
    """Tests for the 100-course deep course library."""

    @pytest.mark.asyncio
    async def test_list_deep_courses_has_100_quality_courses(self, client):
        """GET /api/courses should expose the full 100-course library."""
        resp = await client.get("/api/courses")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 100
        assert len(data["courses"]) == 100
        assert all(course["chapter_count"] >= 5 for course in data["courses"])
        assert all(course["quiz_count"] >= 10 for course in data["courses"])
        assert all(course["audio_status"] == "file_ready" for course in data["courses"])
        assert all(course["audio_file"] in {"audio/intro.m4a", "audio/intro.mp3"} for course in data["courses"])
        assert all(course["audio_duration_seconds"] >= 25 for course in data["courses"])

    @pytest.mark.asyncio
    async def test_deep_course_detail_chapter_and_quiz(self, client):
        """A generated deep course should expose detail, chapter content and quiz."""
        detail = await client.get("/api/courses/belief_audit")
        assert detail.status_code == 200
        detail_data = detail.json()
        assert detail_data["chapter_count"] == 5
        assert detail_data["quiz_count"] == 10
        assert detail_data["audio_status"] == "file_ready"
        assert detail_data["audio_file"] in {"audio/intro.m4a", "audio/intro.mp3"}

        chapter = await client.get("/api/courses/belief_audit/chapters/ch01")
        assert chapter.status_code == 200
        assert "核心信念审计" in chapter.json()["content"]

        quiz = await client.get("/api/courses/belief_audit/chapters/ch01/quiz")
        assert quiz.status_code == 200
        assert len(quiz.json()["questions"]) >= 1
        assert quiz.json()["questions"][0]["answer"] in {"A", "B", "C", "D"}

        cover = await client.get("/api/courses/belief_audit/cover")
        assert cover.status_code == 200
        assert cover.headers["content-type"].startswith("image/svg+xml")

        audio = await client.get("/api/courses/belief_audit/audio")
        assert audio.status_code == 200
        assert audio.headers["content-type"].startswith(("audio/mp4", "audio/mpeg"))

        audio_script = await client.get("/api/courses/belief_audit/audio-script")
        assert audio_script.status_code == 200
        assert "核心信念审计" in audio_script.json()["script"]


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
