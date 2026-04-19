"""
窄门 (NarrowGate) — 数据持久化层 (Database)

SQLite数据库，存储审计记录、穿越进度、用户数据。

架构师：贾维斯 (Jarvis) for 小林医生
"""

import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from contextlib import contextmanager

DB_PATH = Path(__file__).parent.parent.parent / "data" / "narrowgate.db"


class Database:
    """
    窄门数据库

    SQLite持久化存储
    """

    def __init__(self, db_path: str = None):
        self.db_path = str(db_path or DB_PATH)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """初始化数据库表"""
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE,
                    level INTEGER DEFAULT 1,
                    created_at TEXT,
                    last_active TEXT
                );

                CREATE TABLE IF NOT EXISTS audits (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    status TEXT DEFAULT 'in_progress',
                    current_dimension TEXT DEFAULT '认知',
                    current_depth INTEGER DEFAULT 1,
                    shackle_map TEXT DEFAULT '{}',
                    gate_candidates TEXT DEFAULT '[]',
                    started_at TEXT,
                    completed_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS audit_responses (
                    id TEXT PRIMARY KEY,
                    audit_id TEXT,
                    question TEXT,
                    answer TEXT,
                    dimension TEXT,
                    depth_level INTEGER,
                    evasion_detected INTEGER DEFAULT 0,
                    evasion_type TEXT,
                    ai_analysis TEXT,
                    master_id TEXT,
                    created_at TEXT,
                    FOREIGN KEY (audit_id) REFERENCES audits(id)
                );

                CREATE TABLE IF NOT EXISTS crossings (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    gate_id TEXT,
                    gate_name TEXT,
                    status TEXT DEFAULT 'active',
                    current_day INTEGER DEFAULT 0,
                    total_days INTEGER DEFAULT 30,
                    completed INTEGER DEFAULT 0,
                    skipped INTEGER DEFAULT 0,
                    streak INTEGER DEFAULT 0,
                    max_streak INTEGER DEFAULT 0,
                    started_at TEXT,
                    completed_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS daily_records (
                    id TEXT PRIMARY KEY,
                    crossing_id TEXT,
                    day INTEGER,
                    challenge TEXT,
                    difficulty INTEGER,
                    status TEXT DEFAULT 'pending',
                    response TEXT,
                    witness_verified INTEGER DEFAULT 0,
                    created_at TEXT,
                    completed_at TEXT,
                    FOREIGN KEY (crossing_id) REFERENCES crossings(id)
                );

                CREATE TABLE IF NOT EXISTS witnesses (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    name TEXT NOT NULL,
                    email TEXT DEFAULT '',
                    relationship TEXT DEFAULT '朋友',
                    verified INTEGER DEFAULT 0,
                    created_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS witness_verifications (
                    id TEXT PRIMARY KEY,
                    witness_id TEXT,
                    crossing_id TEXT,
                    day INTEGER,
                    challenge TEXT,
                    verified INTEGER DEFAULT 0,
                    message TEXT DEFAULT '',
                    timestamp TEXT,
                    FOREIGN KEY (witness_id) REFERENCES witnesses(id),
                    FOREIGN KEY (crossing_id) REFERENCES crossings(id)
                );

                CREATE TABLE IF NOT EXISTS witness_groups (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    name TEXT NOT NULL,
                    max_members INTEGER DEFAULT 5,
                    created_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS witness_group_members (
                    group_id TEXT,
                    witness_id TEXT,
                    joined_at TEXT,
                    PRIMARY KEY (group_id, witness_id),
                    FOREIGN KEY (group_id) REFERENCES witness_groups(id),
                    FOREIGN KEY (witness_id) REFERENCES witnesses(id)
                );

                CREATE TABLE IF NOT EXISTS divinity_records (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    record_type TEXT,
                    title TEXT,
                    description TEXT,
                    evidence TEXT,
                    dimension TEXT,
                    verified INTEGER DEFAULT 0,
                    created_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS check_ins (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    check_in_date TEXT,
                    streak_count INTEGER DEFAULT 1,
                    max_streak INTEGER DEFAULT 1,
                    created_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                CREATE INDEX IF NOT EXISTS idx_audits_user ON audits(user_id);
                CREATE INDEX IF NOT EXISTS idx_responses_audit ON audit_responses(audit_id);
                CREATE INDEX IF NOT EXISTS idx_crossings_user ON crossings(user_id);
                CREATE INDEX IF NOT EXISTS idx_daily_crossing ON daily_records(crossing_id);
                CREATE INDEX IF NOT EXISTS idx_checkins_user ON check_ins(user_id);
                CREATE INDEX IF NOT EXISTS idx_checkins_date ON check_ins(check_in_date);
            """)

    @contextmanager
    def _connect(self):
        """数据库连接上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    # ============================================================
    # 用户
    # ============================================================

    def create_user(self, username: str = None) -> dict:
        """创建用户（用户名重复时自动生成唯一名称）"""
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        effective_username = username or user_id
        with self._connect() as conn:
            # 检查用户名是否已存在
            existing = conn.execute("SELECT id FROM users WHERE username = ?", (effective_username,)).fetchone()
            if existing:
                effective_username = f"{effective_username}_{uuid.uuid4().hex[:4]}"
            conn.execute(
                "INSERT INTO users (id, username, created_at, last_active) VALUES (?, ?, ?, ?)",
                (user_id, effective_username, now, now),
            )
        return {"id": user_id, "username": effective_username, "level": 1}

    def get_user(self, user_id: str) -> Optional[dict]:
        """获取用户"""
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return dict(row) if row else None

    def update_user_level(self, user_id: str, level: int):
        """更新用户层级"""
        with self._connect() as conn:
            conn.execute("UPDATE users SET level = ? WHERE id = ?", (level, user_id))

    # ============================================================
    # 审计
    # ============================================================

    def create_audit(self, user_id: str) -> str:
        """创建审计记录"""
        audit_id = f"audit_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO audits (id, user_id, started_at) VALUES (?, ?, ?)",
                (audit_id, user_id, now),
            )
        return audit_id

    def get_audit(self, audit_id: str) -> Optional[dict]:
        """获取审计记录"""
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM audits WHERE id = ?", (audit_id,)).fetchone()
            if row:
                d = dict(row)
                d["shackle_map"] = json.loads(d["shackle_map"])
                d["gate_candidates"] = json.loads(d["gate_candidates"])
                return d
            return None

    def update_audit(self, audit_id: str, **kwargs):
        """更新审计记录"""
        fields = []
        values = []
        for k, v in kwargs.items():
            if k in ("shackle_map", "gate_candidates"):
                v = json.dumps(v, ensure_ascii=False)
            fields.append(f"{k} = ?")
            values.append(v)
        values.append(audit_id)
        with self._connect() as conn:
            conn.execute(f"UPDATE audits SET {', '.join(fields)} WHERE id = ?", values)

    def save_audit_response(self, audit_id: str, response: dict) -> str:
        """保存审计回答"""
        resp_id = f"resp_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO audit_responses 
                   (id, audit_id, question, answer, dimension, depth_level, 
                    evasion_detected, evasion_type, ai_analysis, master_id, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    resp_id, audit_id,
                    response.get("question", ""),
                    response.get("answer", ""),
                    response.get("dimension", ""),
                    response.get("depth_level", 1),
                    1 if response.get("evasion_detected") else 0,
                    response.get("evasion_type", ""),
                    response.get("ai_analysis", ""),
                    response.get("master_id", ""),
                    now,
                ),
            )
        return resp_id

    def get_audit_responses(self, audit_id: str) -> List[dict]:
        """获取审计的所有回答"""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM audit_responses WHERE audit_id = ? ORDER BY created_at",
                (audit_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def complete_audit(self, audit_id: str, shackle_map: dict, gate_candidates: list):
        """完成审计"""
        now = datetime.now().isoformat()
        self.update_audit(
            audit_id,
            status="completed",
            completed_at=now,
            shackle_map=shackle_map,
            gate_candidates=gate_candidates,
        )

    # ============================================================
    # 穿越
    # ============================================================

    def create_crossing(self, user_id: str, gate_id: str, gate_name: str) -> str:
        """创建穿越记录"""
        crossing_id = f"cross_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO crossings (id, user_id, gate_id, gate_name, started_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (crossing_id, user_id, gate_id, gate_name, now),
            )
        return crossing_id

    def get_crossing(self, crossing_id: str) -> Optional[dict]:
        """获取穿越记录"""
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM crossings WHERE id = ?", (crossing_id,)).fetchone()
            return dict(row) if row else None

    def get_user_active_crossings(self, user_id: str) -> List[dict]:
        """获取用户的活跃穿越"""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM crossings WHERE user_id = ? AND status = 'active' ORDER BY started_at DESC",
                (user_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def update_crossing(self, crossing_id: str, **kwargs):
        """更新穿越记录"""
        fields = []
        values = []
        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            values.append(v)
        values.append(crossing_id)
        with self._connect() as conn:
            conn.execute(f"UPDATE crossings SET {', '.join(fields)} WHERE id = ?", values)

    def save_daily_record(self, crossing_id: str, record: dict) -> str:
        """保存每日记录"""
        record_id = f"daily_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO daily_records
                   (id, crossing_id, day, challenge, difficulty, status, response, 
                    witness_verified, created_at, completed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record_id, crossing_id,
                    record.get("day", 0),
                    record.get("challenge", ""),
                    record.get("difficulty", 1),
                    record.get("status", "pending"),
                    record.get("response", ""),
                    1 if record.get("witness_verified") else 0,
                    now,
                    record.get("completed_at", ""),
                ),
            )
        return record_id

    def get_daily_records(self, crossing_id: str) -> List[dict]:
        """获取穿越的所有每日记录"""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM daily_records WHERE crossing_id = ? ORDER BY day",
                (crossing_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    # ============================================================
    # 神性档案
    # ============================================================

    def add_divinity_record(self, user_id: str, record: dict) -> str:
        """添加神性记录"""
        record_id = f"div_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO divinity_records
                   (id, user_id, record_type, title, description, evidence, 
                    dimension, verified, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record_id, user_id,
                    record.get("type", "crossing"),
                    record.get("title", ""),
                    record.get("description", ""),
                    record.get("evidence", ""),
                    record.get("dimension", ""),
                    1 if record.get("verified") else 0,
                    now,
                ),
            )
        return record_id

    def get_divinity_records(self, user_id: str) -> List[dict]:
        """获取用户的神性档案"""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM divinity_records WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    # ============================================================
    # 统计
    # ============================================================

    def get_stats(self) -> dict:
        """获取平台统计"""
        with self._connect() as conn:
            users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            audits = conn.execute("SELECT COUNT(*) FROM audits").fetchone()[0]
            completed_audits = conn.execute(
                "SELECT COUNT(*) FROM audits WHERE status = 'completed'"
            ).fetchone()[0]
            crossings = conn.execute("SELECT COUNT(*) FROM crossings").fetchone()[0]
            return {
                "total_users": users,
                "total_audits": audits,
                "completed_audits": completed_audits,
                "active_crossings": crossings,
            }


    # ============================================================
    # 签到系统
    # ============================================================

    def check_in(self, user_id: str) -> dict:
        """
        每日签到
        
        返回：{
            "success": True/False,
            "streak_count": 连续天数,
            "max_streak": 最长连续,
            "is_new_checkin": 是否是今天第一次签到,
            "message": 提示消息
        }
        """
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now().isoformat()
        
        with self._connect() as conn:
            # 检查今天是否已签到
            existing = conn.execute(
                "SELECT * FROM check_ins WHERE user_id = ? AND check_in_date = ?",
                (user_id, today)
            ).fetchone()
            
            if existing:
                return {
                    "success": False,
                    "streak_count": existing["streak_count"],
                    "max_streak": existing["max_streak"],
                    "is_new_checkin": False,
                    "message": "今天已经签到过了"
                }
            
            # 获取昨天的签到记录
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            yesterday_record = conn.execute(
                "SELECT * FROM check_ins WHERE user_id = ? AND check_in_date = ?",
                (user_id, yesterday)
            ).fetchone()
            
            # 计算连续天数
            if yesterday_record:
                streak_count = yesterday_record["streak_count"] + 1
            else:
                streak_count = 1
            
            # 获取用户最长连续记录
            max_streak_result = conn.execute(
                "SELECT MAX(max_streak) as max_streak FROM check_ins WHERE user_id = ?",
                (user_id,)
            ).fetchone()
            max_streak = max(max_streak_result["max_streak"] if max_streak_result["max_streak"] else 0, streak_count)
            
            # 创建签到记录
            checkin_id = f"checkin_{uuid.uuid4().hex[:12]}"
            conn.execute(
                """INSERT INTO check_ins (id, user_id, check_in_date, streak_count, max_streak, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (checkin_id, user_id, today, streak_count, max_streak, now)
            )
            
            return {
                "success": True,
                "streak_count": streak_count,
                "max_streak": max_streak,
                "is_new_checkin": True,
                "message": f"连续签到 {streak_count} 天！"
            }

    def get_checkin_status(self, user_id: str) -> dict:
        """
        获取用户签到状态
        
        返回：{
            "today_checked": 今天是否已签到,
            "streak_count": 当前连续天数,
            "max_streak": 最长连续天数,
            "total_checkins": 总签到次数,
            "last_checkin": 最后签到时间
        }
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        with self._connect() as conn:
            # 检查今天是否已签到
            today_record = conn.execute(
                "SELECT * FROM check_ins WHERE user_id = ? AND check_in_date = ?",
                (user_id, today)
            ).fetchone()
            
            # 获取最新签到记录
            latest_record = conn.execute(
                "SELECT * FROM check_ins WHERE user_id = ? ORDER BY check_in_date DESC LIMIT 1",
                (user_id,)
            ).fetchone()
            
            # 获取总签到次数
            total_checkins = conn.execute(
                "SELECT COUNT(*) FROM check_ins WHERE user_id = ?",
                (user_id,)
            ).fetchone()[0]
            
            # 获取最长连续天数
            max_streak_result = conn.execute(
                "SELECT MAX(max_streak) as max_streak FROM check_ins WHERE user_id = ?",
                (user_id,)
            ).fetchone()
            
            return {
                "today_checked": today_record is not None,
                "streak_count": latest_record["streak_count"] if latest_record else 0,
                "max_streak": max_streak_result["max_streak"] if max_streak_result["max_streak"] else 0,
                "total_checkins": total_checkins,
                "last_checkin": latest_record["created_at"] if latest_record else None
            }

    def get_checkin_history(self, user_id: str, days: int = 30) -> List[dict]:
        """
        获取签到历史记录
        
        返回最近N天的签到记录
        """
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT * FROM check_ins 
                   WHERE user_id = ? AND check_in_date >= ?
                   ORDER BY check_in_date DESC""",
                (user_id, start_date)
            ).fetchall()
            return [dict(r) for r in rows]


# ============================================================
# 导出
# ============================================================

__all__ = ["Database"]
