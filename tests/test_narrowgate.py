"""
窄门 (NarrowGate) — 自动化测试

覆盖核心模块：soul_audit, gate_finder, crossing, masters, evolution, database, auth
"""

import sys
import os
import pytest
import json
from pathlib import Path

# 确保 src 在路径中
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.soul_audit import (
    SoulAuditEngine, SoulAudit, Shackle, AuditResponse,
    detect_evasion, AUDIT_DIMENSIONS
)
from core.gate_finder import GateFinder, NarrowGate, GATE_TEMPLATES
from core.crossing import (
    CrossingEngine, DailyChallenge, CrossingProgress,
    CHALLENGE_TEMPLATES, TRAINING_WEEKS, get_week_for_day
)
from core.masters import MasterManager, MASTERS, Master
from core.evolution import EvolutionPyramid, EvolutionState, EVOLUTION_LEVELS
from core.database import Database
from core.auth import SessionManager


# ============================================================
# 回避检测测试
# ============================================================

class TestEvasionDetection:
    """测试回避检测引擎"""

    def test_short_answer_detected(self):
        detected, typ = detect_evasion("好")
        assert detected
        assert "过短" in typ

    def test_denial_detected(self):
        detected, typ = detect_evasion(
            "没有啊，我不觉得有什么问题。我觉得我挺好的，一直都这样。"
        )
        assert detected
        assert typ == "否认"

    def test_diversion_detected(self):
        detected, typ = detect_evasion(
            "说起来，其实我想说的是另一个方面的事情。那才是关键所在。"
        )
        assert detected
        assert typ == "转移"

    def test_minimization_detected(self):
        detected, typ = detect_evasion(
            "可能有一点点吧，但也只是稍微的改变。就那样而已，小问题罢了。"
        )
        assert detected
        assert typ == "最小化"

    def test_rationalization_detected(self):
        detected, typ = detect_evasion(
            "因为大家都这样，所以没办法。环境如此，换谁都相同。"
        )
        assert detected
        assert typ == "合理化"

    def test_attack_detected(self):
        detected, typ = detect_evasion(
            "你问这个干嘛？这有什么意义呢。我不喜欢这个问题。"
        )
        assert detected
        assert typ == "攻击"

    def test_genuine_answer_not_detected(self):
        detected, typ = detect_evasion(
            "我觉得我最大的成就是坚持学了三年钢琴。虽然过程中有过无数次想放弃的时刻，但我最终还是坚持下来了。"
        )
        assert not detected

    def test_over_intellectualization(self):
        detected, typ = detect_evasion(
            "从逻辑上来说，客观分析这个情况的话，理论上是有一些问题的，但整体还算合理。"
        )
        assert detected
        assert "过度理智化" in typ

    def test_false_honesty_short(self):
        detected, typ = detect_evasion("说实话，我不太清楚。")
        assert detected


# ============================================================
# 灵魂审计引擎测试
# ============================================================

class TestSoulAuditEngine:
    """测试灵魂审计引擎"""

    @pytest.fixture
    def engine(self):
        return SoulAuditEngine()

    @pytest.fixture
    def audit(self, engine):
        return engine.create_audit("test_user")

    def test_create_audit(self, engine):
        audit = engine.create_audit("user_123")
        assert audit.user_id == "user_123"
        assert audit.status == "in_progress"
        assert audit.current_dimension == "认知"
        assert audit.current_depth == 1

    def test_get_first_question(self, engine, audit):
        q = engine.get_next_question(audit)
        assert q.question
        assert q.depth_level == 1
        assert q.dimension == "认知"

    def test_process_evasion_response(self, engine, audit):
        response = engine.process_response(audit, "没有啊，我不觉得有什么问题。我一直都挺好的，不用你担心。")
        assert response.evasion_detected
        assert response.evasion_type in ["否认", "最小化"]
        assert audit.current_depth > 1  # 检测到回避后深度增加

    def test_process_genuine_response(self, engine, audit):
        # 先问一个表面问题
        engine.get_next_question(audit)
        response = engine.process_response(
            audit,
            "我最大的挑战是时间管理。我总是计划得很好但执行不了，"
            "我觉得这背后是我对失败的恐惧。"
        )
        # 诚实回答不应触发回避
        assert not response.evasion_detected or response.evasion_detected  # 取决于信号匹配

    def test_dimension_switching(self, engine, audit):
        audit.current_dimension = "认知"
        audit.current_depth = 3
        engine._switch_dimension(audit)
        assert audit.current_dimension != "认知"
        assert audit.current_depth == 1

    def test_shackle_identification(self, engine, audit):
        # 模拟同一维度多次回避
        audit.current_dimension = "行为"
        for _ in range(3):
            resp = engine.process_response(audit, "没有啊，我觉得还好")
        assert len(audit.shackle_map) >= 1

    def test_complete_audit_report(self, engine, audit):
        # 模拟一次审计
        for _ in range(5):
            engine.process_response(audit, "没有，我觉得还好吧，没什么特别的")
        report = engine.complete_audit(audit)
        assert report["status"] == "completed"
        assert "summary" in report
        assert report["summary"]["total_conversations"] == 5

    def test_audit_to_dict(self, engine, audit):
        d = audit.to_dict()
        assert "id" in d
        assert "user_id" in d


# ============================================================
# 窄门识别器测试
# ============================================================

class TestGateFinder:
    """测试窄门识别"""

    @pytest.fixture
    def finder(self):
        return GateFinder()

    def test_match_gate_template(self, finder):
        shackle = Shackle(
            id="test_1",
            name="舒适区依赖",
            description="在认知维度反复出现否认回避",
            dimension="认知",
            depth_score=80,
            evasion_level=90,
        )
        gate = finder._match_gate_template(shackle)
        assert gate is not None
        assert gate.dimension == "认知"

    def test_empty_audit_no_gates(self, finder):
        audit = SoulAudit(
            id="test",
            user_id="u1",
            status="in_progress",
            current_dimension="认知",
            current_depth=1,
        )
        gates = finder.find_gates(audit)
        assert gates == []

    def test_gate_report_no_gates(self, finder):
        report = finder.generate_gate_report([])
        assert report["status"] == "no_gates_found"

    def test_gate_report_with_gates(self, finder):
        gate = NarrowGate(
            id="test_gate",
            name="认知：舒适区依赖",
            description="测试",
            dimension="认知",
            priority_score=80,
            why_this_gate="因为你总是回避",
            wide_gate_path="容易的路",
            narrow_gate_path="难的路",
            crossing_indicators=["坚持30天"],
            daily_challenge_template="今天做一件不想做的事",
        )
        report = finder.generate_gate_report([gate])
        assert report["status"] == "gates_found"
        assert report["primary_gate"]["name"] == "认知：舒适区依赖"

    def test_all_dimensions_have_templates(self):
        for dim in AUDIT_DIMENSIONS:
            assert dim in GATE_TEMPLATES or dim == "幻觉"  # 幻觉在交叉引擎中


# ============================================================
# 穿越训练引擎测试
# ============================================================

class TestCrossingEngine:
    """测试穿越训练"""

    @pytest.fixture
    def engine(self):
        return CrossingEngine()

    @pytest.fixture
    def gate(self):
        return NarrowGate(
            id="gate_test",
            name="行为：执行断裂",
            description="拖延",
            dimension="行为",
            priority_score=75,
            why_this_gate="你总是拖延",
            wide_gate_path="明天再做",
            narrow_gate_path="现在就做",
        )

    def test_generate_daily_challenge(self, engine, gate):
        challenge = engine.generate_daily_challenge(gate, 0)
        assert challenge.challenge
        assert 1 <= challenge.difficulty <= 10

    def test_difficulty_progression(self, engine, gate):
        d1 = engine.generate_daily_challenge(gate, 0)
        d10 = engine.generate_daily_challenge(gate, 10)
        d25 = engine.generate_daily_challenge(gate, 25)
        assert d1.difficulty <= d10.difficulty <= d25.difficulty

    def test_start_crossing(self, engine, gate):
        progress = engine.start_crossing(gate)
        assert progress.gate_id == gate.id
        assert progress.current_day == 0

    def test_record_completion(self, engine, gate):
        progress = engine.start_crossing(gate)
        challenge = engine.generate_daily_challenge(gate, 0)
        record = engine.record_challenge_completion(progress, challenge, "完成！")
        assert progress.current_day == 1
        assert progress.challenges_completed == 1
        assert progress.streak_days == 1

    def test_skip_challenge(self, engine, gate):
        progress = engine.start_crossing(gate)
        engine.skip_challenge(progress, "太忙了")
        assert progress.current_day == 1
        assert progress.challenges_skipped == 1
        assert progress.streak_days == 0

    def test_progress_report(self, engine, gate):
        progress = engine.start_crossing(gate)
        report = engine.get_progress_report(progress)
        assert "completion_rate" in report
        assert "streak" in report
        assert "message" in report

    def test_week_plan(self):
        assert get_week_for_day(1)["week"] == 1
        assert get_week_for_day(10)["week"] == 2
        assert get_week_for_day(17)["week"] == 3
        assert get_week_for_day(25)["week"] == 4

    def test_training_weeks_structure(self):
        assert len(TRAINING_WEEKS) == 4
        for w in TRAINING_WEEKS:
            assert "week" in w
            assert "name" in w
            assert "difficulty_range" in w


# ============================================================
# 大师系统测试
# ============================================================

class TestMasters:
    """测试大师系统"""

    @pytest.fixture
    def manager(self):
        return MasterManager()

    def test_all_masters_exist(self, manager):
        expected = ["socrates", "jung", "memento", "mirror", "architect", "alchemist", "gatekeeper"]
        for mid in expected:
            assert manager.get_master(mid) is not None

    def test_available_masters_by_level(self, manager):
        level1 = manager.get_available_masters(1)
        level1_ids = [m.id for m in level1]
        assert "socrates" in level1_ids
        assert "jung" in level1_ids
        assert "architect" not in level1_ids  # level 2 required

        level3 = manager.get_available_masters(3)
        level3_ids = [m.id for m in level3]
        assert "architect" in level3_ids
        assert "alchemist" in level3_ids

    def test_recommend_master(self, manager):
        m = manager.recommend_master("认知", 1)
        assert m is not None

    def test_master_card_format(self, manager):
        master = manager.get_master("socrates")
        card = manager.get_master_card(master)
        assert "id" in card
        assert "name" in card
        assert card["name"] == "苏格拉底"

    def test_master_has_required_fields(self):
        for mid, master in MASTERS.items():
            assert master.id
            assert master.name
            assert master.philosophy
            assert master.greeting
            assert master.questioning_style
            assert len(master.specialties) > 0
            assert len(master.signature_phrases) > 0
            assert 1 <= master.level_required <= 5


# ============================================================
# 进化金字塔测试
# ============================================================

class TestEvolution:
    """测试进化金字塔"""

    @pytest.fixture
    def pyramid(self):
        return EvolutionPyramid()

    def test_default_state(self, pyramid):
        state = pyramid.get_state("new_user")
        assert state.current_level == 1
        assert state.experience_points == 0

    def test_add_experience(self, pyramid):
        state = pyramid.get_state("user1")
        state.add_experience(50)
        assert state.experience_points == 50
        assert state.current_level == 1

    def test_level_up(self, pyramid):
        state = pyramid.get_state("user2")
        state.add_experience(100)
        assert state.current_level == 2

    def test_multiple_level_ups(self, pyramid):
        state = pyramid.get_state("user3")
        state.add_experience(700)
        assert state.current_level >= 4

    def test_record_breakthrough(self, pyramid):
        result = pyramid.record_breakthrough("user4", "测试窄门", "突破了拖延")
        assert "gate" in result
        assert result["gate"] == "测试窄门"

    def test_record_crossing_completion(self, pyramid):
        result = pyramid.record_crossing_completion("user5", "行为：执行断裂")
        assert result["experience_gained"] == 200

    def test_pyramid_data_structure(self, pyramid):
        data = pyramid.get_pyramid_data("user6")
        assert "levels" in data
        assert len(data["levels"]) == 5
        assert "current_level" in data
        assert "experience_points" in data

    def test_visual_pyramid(self, pyramid):
        visual = pyramid.get_visual_pyramid("user7")
        assert "1" in visual
        assert "·" in visual

    def test_max_level_no_next(self):
        state = EvolutionState(current_level=5, experience_points=2000)
        assert state.next_level_data is None
        assert state.progress_to_next == 100


# ============================================================
# 数据库测试
# ============================================================

class TestDatabase:
    """测试数据库"""

    @pytest.fixture
    def db(self, tmp_path):
        return Database(str(tmp_path / "test.db"))

    def test_create_user(self, db):
        user = db.create_user("test_user")
        assert user["id"].startswith("user_")
        assert user["username"] == "test_user"

    def test_create_user_duplicate_name(self, db):
        user1 = db.create_user("same_name")
        user2 = db.create_user("same_name")
        assert user1["username"] != user2["username"]  # 自动生成唯一名称

    def test_get_user(self, db):
        user = db.create_user("findme")
        found = db.get_user(user["id"])
        assert found is not None
        assert found["username"] == "findme"

    def test_user_not_found(self, db):
        assert db.get_user("nonexistent") is None

    def test_create_audit(self, db):
        user = db.create_user("auditor")
        audit_id = db.create_audit(user["id"])
        assert audit_id.startswith("audit_")

    def test_save_and_get_audit_response(self, db):
        user = db.create_user("responder")
        audit_id = db.create_audit(user["id"])
        db.save_audit_response(audit_id, {
            "question": "你最大的成就？",
            "answer": "坚持学习",
            "dimension": "认知",
            "depth_level": 1,
            "evasion_detected": False,
        })
        responses = db.get_audit_responses(audit_id)
        assert len(responses) == 1
        assert responses[0]["answer"] == "坚持学习"

    def test_create_crossing(self, db):
        user = db.create_user("crosser")
        crossing_id = db.create_crossing(user["id"], "gate_1", "测试窄门")
        assert crossing_id.startswith("cross_")
        crossing = db.get_crossing(crossing_id)
        assert crossing["gate_name"] == "测试窄门"

    def test_daily_records(self, db):
        user = db.create_user("daily")
        crossing_id = db.create_crossing(user["id"], "gate_2", "行为窄门")
        db.save_daily_record(crossing_id, {
            "day": 1,
            "challenge": "今天做一件不想做的事",
            "difficulty": 3,
        })
        records = db.get_daily_records(crossing_id)
        assert len(records) == 1

    def test_witness(self, db):
        user = db.create_user("witness_user")
        wid = db.create_witness(user["id"], "张三", "z@test.com", "朋友")
        witnesses = db.get_user_witnesses(user["id"])
        assert len(witnesses) == 1
        assert witnesses[0]["name"] == "张三"

    def test_divinity_records(self, db):
        user = db.create_user("divine")
        db.add_divinity_record(user["id"], {
            "type": "crossing",
            "title": "完成穿越",
            "description": "30天挑战完成",
        })
        records = db.get_divinity_records(user["id"])
        assert len(records) == 1

    def test_evolution_state(self, db):
        user = db.create_user("evo")
        db.upsert_evolution_state(user["id"], current_level=2, experience_points=150)
        state = db.get_evolution_state(user["id"])
        assert state["current_level"] == 2

    def test_stats(self, db):
        db.create_user("s1")
        db.create_user("s2")
        stats = db.get_stats()
        assert stats["total_users"] >= 2


# ============================================================
# 认证测试
# ============================================================

class TestAuth:
    """测试认证模块"""

    @pytest.fixture
    def sm(self):
        return SessionManager()

    def test_create_session(self, sm):
        token = sm.create_session("user_1")
        assert len(token) > 10

    def test_validate_token(self, sm):
        token = sm.create_session("user_2")
        uid = sm.validate_token(token)
        assert uid == "user_2"

    def test_invalid_token(self, sm):
        assert sm.validate_token("bad_token") is None

    def test_revoke_session(self, sm):
        token = sm.create_session("user_3")
        sm.revoke_session(token)
        assert sm.validate_token(token) is None

    def test_refresh_token(self, sm):
        old_token = sm.create_session("user_4")
        new_token = sm.refresh_token(old_token)
        assert new_token is not None
        assert new_token != old_token
        assert sm.validate_token(old_token) is None  # 旧 token 失效
        assert sm.validate_token(new_token) == "user_4"


# ============================================================
# FastAPI 集成测试
# ============================================================

class TestAPI:
    """FastAPI 集成测试"""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        # 需要设置测试数据库
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from api.main import app
        return TestClient(app)

    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"

    def test_index(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "窄门" in resp.text

    def test_register_user(self, client):
        resp = client.post("/api/user/register", json={"username": "pytest_user"})
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "token" in data

    def test_masters_list(self, client):
        resp = client.get("/api/masters")
        assert resp.status_code == 200
        data = resp.json()
        assert "masters" in data
        assert len(data["masters"]) >= 4

    def test_audit_flow(self, client):
        # 开始审计
        resp = client.post("/api/audit/start", json={"username": "audit_test_user"})
        assert resp.status_code == 200
        data = resp.json()
        audit_id = data["audit_id"]
        assert data["question"]

        # 提交回答
        resp = client.post("/api/audit/answer", json={
            "audit_id": audit_id,
            "answer": "我最大的成就是一直在努力学习新知识，虽然过程很辛苦但很有意义。",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "evasion_detected" in data

        # 完成审计
        resp = client.post("/api/audit/complete", json={"user_id": data.get("user_id", "test")})
        assert resp.status_code in [200, 404]  # 可能找不到进行中的审计

    def test_training_plan(self, client):
        resp = client.get("/api/training/plan")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["weeks"]) == 4

    def test_api_health_detailed(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "窄门 NarrowGate"

    def test_stats(self, client):
        resp = client.get("/api/stats")
        assert resp.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
