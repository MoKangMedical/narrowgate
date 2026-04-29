"""
窄门 (NarrowGate) — Shared Test Fixtures

Provides reusable fixtures for all test modules.
"""

import os
import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Ensure src is on the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ============================================================
# Database Fixtures
# ============================================================

@pytest.fixture
def tmp_db(tmp_path):
    """Provide a temporary SQLite database for testing."""
    db_path = str(tmp_path / "test_narrowgate.db")
    from core.database import Database
    db = Database(db_path=db_path)
    return db


@pytest.fixture
def sample_user(tmp_db):
    """Create and return a sample user."""
    user = tmp_db.create_user("test_user")
    return user


# ============================================================
# Core Engine Fixtures
# ============================================================

@pytest.fixture
def audit_engine():
    """Provide a fresh SoulAuditEngine instance."""
    from core.soul_audit import SoulAuditEngine
    return SoulAuditEngine()


@pytest.fixture
def gate_finder():
    """Provide a GateFinder instance."""
    from core.gate_finder import GateFinder
    return GateFinder()


@pytest.fixture
def crossing_engine():
    """Provide a CrossingEngine instance."""
    from core.crossing import CrossingEngine
    return CrossingEngine()


@pytest.fixture
def master_manager():
    """Provide a MasterManager instance."""
    from core.masters import MasterManager
    return MasterManager()


@pytest.fixture
def witness_network():
    """Provide a WitnessNetwork instance."""
    from core.witness import WitnessNetwork
    return WitnessNetwork()


@pytest.fixture
def evolution_pyramid():
    """Provide an EvolutionPyramid instance."""
    from core.evolution import EvolutionPyramid
    return EvolutionPyramid()


# ============================================================
# MIMO Client Fixtures
# ============================================================

@pytest.fixture
def mock_mimo_client():
    """Provide a mocked MIMO client that returns canned responses."""
    from core.mimo_client import MIMOClient, MIMOConfig
    config = MIMOConfig(api_key="test-key")
    client = MIMOClient(config)

    # Patch the chat method to return a canned response
    with patch.object(client, "chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = "This is a test AI response."
        with patch.object(client, "master_converse", new_callable=AsyncMock) as mock_converse:
            mock_converse.return_value = "Master response for testing."
            with patch.object(client, "soul_audit_question", new_callable=AsyncMock) as mock_audit:
                mock_audit.return_value = "Follow-up question for testing."
                yield client


# ============================================================
# API / FastAPI Fixtures
# ============================================================

@pytest.fixture
def test_client():
    """Provide a FastAPI test client."""
    from httpx import AsyncClient, ASGITransport

    # We need to mock MIMO to avoid real API calls in tests
    with patch.dict(os.environ, {"MIMO_API_KEY": "test-key"}):
        # Import app after env setup
        from api.main import app

        transport = ASGITransport(app=app)
        return AsyncClient(transport=transport, base_url="http://test")


# ============================================================
# Sample Data Fixtures
# ============================================================

@pytest.fixture
def sample_audit():
    """Provide a sample SoulAudit object."""
    from core.soul_audit import SoulAudit, Shackle, AUDIT_DIMENSIONS
    audit = SoulAudit(
        id="test_audit_001",
        user_id="test_user_001",
        status="in_progress",
        current_dimension="认知",
        current_depth=1,
    )
    return audit


@pytest.fixture
def sample_shackle():
    """Provide a sample Shackle object."""
    from core.soul_audit import Shackle
    return Shackle(
        id="shackle_001",
        name="Fear of Failure",
        description="Avoiding challenges due to fear of failing",
        dimension="认知",
        depth_score=75.0,
        evasion_level=80.0,
        evidence=["Avoided applying for promotion"],
    )


@pytest.fixture
def sample_gate():
    """Provide a sample NarrowGate object."""
    from core.gate_finder import NarrowGate
    return NarrowGate(
        id="gate_test_001",
        name="Fear of Public Speaking",
        description="Avoiding public speaking despite career impact",
        dimension="行为",
        priority_score=85.0,
        why_this_gate="High avoidance, high growth leverage",
        wide_gate_path="Stay silent in meetings",
        narrow_gate_path="Volunteer to present at next team meeting",
        estimated_crossing_days=30,
    )
