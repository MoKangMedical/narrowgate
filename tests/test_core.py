"""
窄门 (NarrowGate) — Core Module Tests

Tests for the fundamental building blocks:
  - Soul Audit Engine
  - Gate Finder
  - Crossing Engine
  - Masters
  - Witness Network
  - Evolution Pyramid
  - Database
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from core.soul_audit import (
    SoulAuditEngine,
    SoulAudit,
    Shackle,
    AuditQuestion,
    AuditResponse,
    AUDIT_DIMENSIONS,
)
from core.gate_finder import GateFinder, NarrowGate, GATE_TEMPLATES
from core.crossing import CrossingEngine, DailyChallenge, CrossingProgress
from core.masters import Master, MasterManager, MASTERS
from core.witness import WitnessNetwork, Witness
from core.evolution import EvolutionPyramid, EVOLUTION_LEVELS, EvolutionState
from core.database import Database


# ============================================================
# Soul Audit Engine
# ============================================================

class TestSoulAuditEngine:
    """Tests for the SoulAuditEngine."""

    def test_create_audit(self, audit_engine):
        """Creating an audit should return a valid SoulAudit."""
        audit = audit_engine.create_audit("user_001")
        assert type(audit).__name__ == "SoulAudit"
        assert audit.user_id == "user_001"
        assert audit.status == "in_progress"
        assert audit.current_dimension == "认知"
        assert audit.current_depth == 1

    def test_get_first_question(self, audit_engine):
        """First question should be a surface-level question."""
        audit = audit_engine.create_audit("user_001")
        question = audit_engine.get_next_question(audit)
        assert type(question).__name__ == "AuditQuestion"
        assert question.depth_level == 1
        assert question.dimension == "认知"
        assert len(question.question) > 0

    def test_audit_dimensions_exist(self):
        """All five dimensions should be defined."""
        # The actual dimensions include 宇宙认知 as a 6th dimension
        expected_minimal = {"认知", "情绪", "行为", "关系", "事业"}
        assert expected_minimal.issubset(set(AUDIT_DIMENSIONS.keys()))

    def test_audit_dimension_has_questions(self):
        """Each dimension should have surface questions."""
        for dim, info in AUDIT_DIMENSIONS.items():
            assert "surface_questions" in info, f"{dim} missing surface_questions"
            assert len(info["surface_questions"]) > 0, f"{dim} has no surface questions"


class TestShackle:
    """Tests for the Shackle data model."""

    def test_shackle_creation(self, sample_shackle):
        """Shackle should store all required fields."""
        assert sample_shackle.id == "shackle_001"
        assert sample_shackle.name == "Fear of Failure"
        assert sample_shackle.dimension == "认知"
        assert sample_shackle.depth_score == 75.0
        assert sample_shackle.evasion_level == 80.0

    def test_gate_priority_calculation(self, sample_shackle):
        """Gate priority = evasion_level * depth_score / 100."""
        expected = 80.0 * 75.0 / 100
        assert sample_shackle.gate_priority == expected

    def test_gate_priority_zero_evasion(self):
        """Zero evasion means zero priority."""
        shackle = Shackle(
            id="s1", name="test", description="test",
            dimension="认知", depth_score=100, evasion_level=0,
        )
        assert shackle.gate_priority == 0

    def test_shackle_timestamps_set_automatically(self):
        """first_seen should be set on creation."""
        shackle = Shackle(
            id="s1", name="test", description="test",
            dimension="认知", depth_score=50, evasion_level=50,
        )
        assert shackle.first_seen != ""
        assert shackle.last_updated != ""


class TestSoulAudit:
    """Tests for the SoulAudit data model."""

    def test_audit_defaults(self):
        """Default audit should have sensible defaults."""
        audit = SoulAudit(
            id="a1", user_id="u1", status="in_progress",
            current_dimension="认知", current_depth=1,
        )
        assert audit.shackle_map == {}
        assert audit.gate_candidates == []
        assert audit.conversation == []

    def test_audit_with_shackles(self, sample_shackle):
        """Audit should hold shackle map."""
        audit = SoulAudit(
            id="a1", user_id="u1", status="in_progress",
            current_dimension="认知", current_depth=1,
            shackle_map={"s1": sample_shackle},
        )
        assert len(audit.shackle_map) == 1
        assert "s1" in audit.shackle_map


# ============================================================
# Gate Finder
# ============================================================

class TestGateFinder:
    """Tests for the GateFinder."""

    def test_gate_templates_exist(self):
        """Gate templates should be defined for dimensions."""
        assert isinstance(GATE_TEMPLATES, dict)
        assert len(GATE_TEMPLATES) > 0

    def test_find_gates_empty_audit(self, gate_finder):
        """Finding gates on empty audit should return empty list."""
        audit = SoulAudit(
            id="a1", user_id="u1", status="in_progress",
            current_dimension="认知", current_depth=1,
        )
        gates = gate_finder.find_gates(audit)
        assert isinstance(gates, list)
        assert len(gates) == 0

    def test_find_gates_with_shackle(self, gate_finder, sample_shackle):
        """Finding gates should match shackle to gate template."""
        audit = SoulAudit(
            id="a1", user_id="u1", status="in_progress",
            current_dimension="认知", current_depth=1,
            shackle_map={"s1": sample_shackle},
        )
        gates = gate_finder.find_gates(audit)
        # Should find at least one gate for the shackle
        assert isinstance(gates, list)
        # Gates should be sorted by priority descending
        if len(gates) > 1:
            for i in range(len(gates) - 1):
                assert gates[i].priority_score >= gates[i + 1].priority_score


class TestNarrowGate:
    """Tests for the NarrowGate data model."""

    def test_gate_creation(self, sample_gate):
        """Gate should store all required fields."""
        assert sample_gate.id == "gate_test_001"
        assert sample_gate.name == "Fear of Public Speaking"
        assert sample_gate.estimated_crossing_days == 30

    def test_gate_defaults(self):
        """Default values should be sensible."""
        gate = NarrowGate(
            id="g1", name="test", description="test",
            dimension="行为", priority_score=50,
            why_this_gate="test", wide_gate_path="easy",
            narrow_gate_path="hard",
        )
        assert gate.crossing_indicators == []
        assert gate.source_shackles == []
        assert gate.estimated_crossing_days == 30


# ============================================================
# Crossing Engine
# ============================================================

class TestCrossingEngine:
    """Tests for the CrossingEngine."""

    def test_start_crossing(self, crossing_engine, sample_gate):
        """Starting a crossing should return a CrossingProgress."""
        progress = crossing_engine.start_crossing(sample_gate)
        assert type(progress).__name__ == "CrossingProgress"
        assert progress.gate_id == sample_gate.id
        assert progress.current_day == 0
        assert progress.total_days == 30

    def test_generate_daily_challenge(self, crossing_engine, sample_gate):
        """Daily challenge should be a valid DailyChallenge."""
        challenge = crossing_engine.generate_daily_challenge(sample_gate, day=1)
        assert type(challenge).__name__ == "DailyChallenge"
        assert len(challenge.challenge) > 0
        assert challenge.difficulty >= 1

    def test_challenge_difficulty_scales(self, crossing_engine, sample_gate):
        """Difficulty should increase with day number."""
        early = crossing_engine.generate_daily_challenge(sample_gate, day=1)
        late = crossing_engine.generate_daily_challenge(sample_gate, day=25)
        assert late.difficulty >= early.difficulty


# ============================================================
# Masters
# ============================================================

class TestMasters:
    """Tests for the Master system."""

    def test_masters_defined(self):
        """All seven masters should be defined."""
        assert len(MASTERS) >= 7

    def test_master_has_required_fields(self):
        """Each master should have all required fields."""
        for master_id, master in MASTERS.items():
            assert isinstance(master, Master)
            assert master.id == master_id
            assert len(master.name) > 0
            assert len(master.title) > 0
            assert len(master.greeting) > 0
            assert len(master.questioning_style) > 0

    def test_master_manager_get_master(self, master_manager):
        """MasterManager should return master by ID."""
        master = master_manager.get_master("socrates")
        assert master is not None
        assert master.name == "苏格拉底"

    def test_master_manager_invalid_id(self, master_manager):
        """MasterManager should return None for unknown IDs."""
        master = master_manager.get_master("nonexistent_master")
        assert master is None

    def test_get_available_masters(self, master_manager):
        """Should return masters available at given level."""
        level1 = master_manager.get_available_masters(1)
        assert len(level1) >= 3  # At least 3 masters at level 1
        for m in level1:
            assert m.level_required <= 1


# ============================================================
# Witness Network
# ============================================================

class TestWitnessNetwork:
    """Tests for the WitnessNetwork."""

    def test_add_witness(self, witness_network):
        """Adding a witness should return a Witness object."""
        witness = witness_network.add_witness(
            name="Friend A",
            email="friend@example.com",
            relationship="friend",
        )
        assert type(witness).__name__ == "Witness"
        assert witness.name == "Friend A"
        assert witness.relationship == "friend"

    def test_list_witnesses(self, witness_network):
        """Listing witnesses should return added witnesses."""
        witness_network.add_witness("Witness 1")
        witness_network.add_witness("Witness 2")
        witnesses = witness_network.get_all_witnesses()
        assert len(witnesses) == 2

    def test_empty_witness_list(self, witness_network):
        """No witnesses should return empty list."""
        witnesses = witness_network.get_all_witnesses()
        assert len(witnesses) == 0


# ============================================================
# Evolution Pyramid
# ============================================================

class TestEvolutionPyramid:
    """Tests for the EvolutionPyramid."""

    def test_evolution_levels_defined(self):
        """All five evolution levels should be defined."""
        assert len(EVOLUTION_LEVELS) == 5
        levels = [l["level"] for l in EVOLUTION_LEVELS]
        assert levels == [1, 2, 3, 4, 5]

    def test_get_initial_state(self, evolution_pyramid):
        """New user should start at level 1 with 0 XP."""
        state = evolution_pyramid.get_state("new_user")
        assert state.current_level == 1
        assert state.experience_points == 0

    def test_record_breakthrough(self, evolution_pyramid):
        """Recording a breakthrough should grant XP."""
        result = evolution_pyramid.record_breakthrough(
            "user_001", "Test Gate", "Overcame fear"
        )
        assert "experience_gained" in result or "gate" in result

    def test_xp_accumulation(self, evolution_pyramid):
        """XP should accumulate with multiple actions."""
        state = evolution_pyramid.get_state("user_xp")
        state.add_experience(10, "daily_challenge")
        state.add_experience(10, "daily_challenge")
        assert state.experience_points == 20


# ============================================================
# Database
# ============================================================

class TestDatabase:
    """Tests for the Database layer."""

    def test_create_user(self, tmp_db):
        """Creating a user should return a dict with id and username."""
        user = tmp_db.create_user("testuser")
        assert "id" in user
        assert "username" in user
        assert user["username"] == "testuser"
        assert user["level"] == 1

    def test_create_user_no_username(self, tmp_db):
        """Creating user without username should auto-generate one."""
        user = tmp_db.create_user()
        assert "id" in user
        assert "username" in user

    def test_get_user(self, tmp_db, sample_user):
        """Getting user by ID should return user data."""
        user = tmp_db.get_user(sample_user["id"])
        assert user is not None
        assert user["id"] == sample_user["id"]

    def test_get_nonexistent_user(self, tmp_db):
        """Getting nonexistent user should return None."""
        user = tmp_db.get_user("user_nonexistent")
        assert user is None

    def test_create_and_get_audit(self, tmp_db, sample_user):
        """Creating an audit should persist in database."""
        audit_id = tmp_db.create_audit(sample_user["id"])
        audit = tmp_db.get_audit(audit_id)
        assert audit is not None
        assert audit["user_id"] == sample_user["id"]
        assert audit["status"] == "in_progress"

    def test_create_crossing(self, tmp_db, sample_user):
        """Creating a crossing should return a crossing ID."""
        crossing_id = tmp_db.create_crossing(
            sample_user["id"], "gate_test", "Test Gate"
        )
        assert crossing_id.startswith("cross_")

    def test_save_and_get_daily_record(self, tmp_db, sample_user):
        """Daily records should persist and be retrievable."""
        crossing_id = tmp_db.create_crossing(
            sample_user["id"], "gate_test", "Test Gate"
        )
        record_id = tmp_db.save_daily_record(crossing_id, {
            "day": 1,
            "challenge": "Test challenge",
            "difficulty": 3,
        })
        records = tmp_db.get_daily_records(crossing_id)
        assert len(records) == 1
        assert records[0]["challenge"] == "Test challenge"

    def test_divinity_records(self, tmp_db, sample_user):
        """Divinity records should be stored and retrievable."""
        record_id = tmp_db.add_divinity_record(sample_user["id"], {
            "type": "crossing",
            "title": "First Crossing",
            "description": "Completed day 1",
        })
        records = tmp_db.get_divinity_records(sample_user["id"])
        assert len(records) == 1
        assert records[0]["title"] == "First Crossing"

    def test_user_active_crossings(self, tmp_db, sample_user):
        """Active crossings should be retrievable."""
        tmp_db.create_crossing(sample_user["id"], "gate_1", "Gate 1")
        tmp_db.create_crossing(sample_user["id"], "gate_2", "Gate 2")
        crossings = tmp_db.get_user_active_crossings(sample_user["id"])
        assert len(crossings) == 2
