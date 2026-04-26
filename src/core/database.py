"""
窄门 (NarrowGate) — 数据持久化层 (Database)

SQLite数据库，存储审计记录、穿越进度、用户数据。

架构师：贾维斯 (Jarvis) for 小林医生
"""

import json
import sqlite3
import uuid
from datetime import datetime
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
                    email TEXT UNIQUE,
                    password_hash TEXT,
                    nickname TEXT,
                    avatar TEXT,
                    wechat_openid TEXT UNIQUE,
                    phone TEXT,
                    level INTEGER DEFAULT 1,
                    experience_points INTEGER DEFAULT 0,
                    subscription_type TEXT DEFAULT 'free',
                    subscription_expires TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    last_login TEXT,
                    last_active TEXT,
                    is_active INTEGER DEFAULT 1,
                    settings TEXT DEFAULT '{}'
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

                CREATE TABLE IF NOT EXISTS learning_journals (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    day INTEGER,
                    content TEXT,
                    mood TEXT,
                    tags TEXT DEFAULT '[]',
                    is_private INTEGER DEFAULT 1,
                    created_at TEXT,
                    updated_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (day) REFERENCES daily_records(day)
                );

                CREATE TABLE IF NOT EXISTS rewards (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    reward_type TEXT,
                    reward_name TEXT,
                    xp_amount INTEGER,
                    badge_id TEXT,
                    description TEXT,
                    created_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS badges (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    icon TEXT,
                    requirement TEXT,
                    created_at TEXT
                );

                CREATE TABLE IF NOT EXISTS user_badges (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    badge_id TEXT,
                    earned_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (badge_id) REFERENCES badges(id)
                );

                CREATE INDEX IF NOT EXISTS idx_audits_user ON audits(user_id);
                CREATE INDEX IF NOT EXISTS idx_responses_audit ON audit_responses(audit_id);
                CREATE INDEX IF NOT EXISTS idx_crossings_user ON crossings(user_id);
                CREATE INDEX IF NOT EXISTS idx_daily_crossing ON daily_records(crossing_id);
                CREATE INDEX IF NOT EXISTS idx_journals_user_day ON learning_journals(user_id, day);
                CREATE INDEX IF NOT EXISTS idx_rewards_user ON rewards(user_id);
                CREATE INDEX IF NOT EXISTS idx_user_badges_user ON user_badges(user_id);
                
                CREATE TABLE IF NOT EXISTS payment_orders (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    payment_method TEXT NOT NULL,
                    trade_no TEXT,
                    status TEXT DEFAULT 'pending',
                    description TEXT,
                    refund_reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    paid_at TIMESTAMP,
                    refunded_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
                CREATE INDEX IF NOT EXISTS idx_payment_user ON payment_orders(user_id);
                CREATE INDEX IF NOT EXISTS idx_payment_status ON payment_orders(status);
            """)
            
            # 初始化默认徽章
            self._init_default_badges(conn)

    def _init_default_badges(self, conn):
        """初始化默认徽章"""
        default_badges = [
            ("persistent_7", "坚持不懈", "连续7天完成挑战", "🔥", "连续7天"),
            ("persistent_14", "意志坚定", "连续14天完成挑战", "💪", "连续14天"),
            ("persistent_21", "钢铁意志", "连续21天完成挑战", "⚔️", "连续21天"),
            ("week_1", "初级穿越者", "完成第一周课程", "🚶", "完成第7天"),
            ("week_2", "中级穿越者", "完成第二周课程", "🏃", "完成第14天"),
            ("week_3", "高级穿越者", "完成第三周课程", "🦸", "完成第21天"),
            ("complete", "封神者", "完成30天穿越训练", "👑", "完成第30天"),
            ("journal_10", "日记达人", "写满10篇学习日记", "📝", "写10篇日记"),
            ("journal_20", "反思大师", "写满20篇学习日记", "📚", "写20篇日记"),
            ("first_crossing", "首次穿越", "完成第一次穿越", "🌟", "完成第1天"),
        ]
        
        for badge_id, name, description, icon, requirement in default_badges:
            # 检查徽章是否已存在
            existing = conn.execute(
                "SELECT id FROM badges WHERE id = ?",
                (badge_id,)
            ).fetchone()
            
            if not existing:
                now = datetime.now().isoformat()
                conn.execute(
                    "INSERT INTO badges (id, name, description, icon, requirement, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (badge_id, name, description, icon, requirement, now)
                )

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
    # 学习日记
    # ============================================================

    def save_journal(self, user_id: str, day: int, content: str, mood: str = None, tags: List[str] = None, is_private: bool = True) -> str:
        """保存学习日记"""
        journal_id = f"journal_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        tags_json = json.dumps(tags or [])
        
        with self._connect() as conn:
            # 检查是否已有该天的日记
            existing = conn.execute(
                "SELECT id FROM learning_journals WHERE user_id = ? AND day = ?",
                (user_id, day)
            ).fetchone()
            
            if existing:
                # 更新现有日记
                conn.execute(
                    """UPDATE learning_journals 
                       SET content = ?, mood = ?, tags = ?, is_private = ?, updated_at = ?
                       WHERE user_id = ? AND day = ?""",
                    (content, mood, tags_json, 1 if is_private else 0, now, user_id, day)
                )
                journal_id = existing["id"]
            else:
                # 创建新日记
                conn.execute(
                    """INSERT INTO learning_journals 
                       (id, user_id, day, content, mood, tags, is_private, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (journal_id, user_id, day, content, mood, tags_json, 1 if is_private else 0, now, now)
                )
        
        return journal_id

    def get_journal(self, user_id: str, day: int) -> Optional[dict]:
        """获取指定天的学习日记"""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM learning_journals WHERE user_id = ? AND day = ?",
                (user_id, day)
            ).fetchone()
            if row:
                result = dict(row)
                result["tags"] = json.loads(result.get("tags", "[]"))
                return result
            return None

    def get_user_journals(self, user_id: str, limit: int = 30) -> List[dict]:
        """获取用户的所有学习日记"""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM learning_journals WHERE user_id = ? ORDER BY day DESC LIMIT ?",
                (user_id, limit)
            ).fetchall()
            results = []
            for row in rows:
                result = dict(row)
                result["tags"] = json.loads(result.get("tags", "[]"))
                results.append(result)
            return results

    def delete_journal(self, user_id: str, day: int) -> bool:
        """删除指定天的学习日记"""
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM learning_journals WHERE user_id = ? AND day = ?",
                (user_id, day)
            )
            return cursor.rowcount > 0

    def get_journal_stats(self, user_id: str) -> dict:
        """获取用户日记统计"""
        with self._connect() as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM learning_journals WHERE user_id = ?",
                (user_id,)
            ).fetchone()[0]
            
            moods = conn.execute(
                """SELECT mood, COUNT(*) as count 
                   FROM learning_journals 
                   WHERE user_id = ? AND mood IS NOT NULL 
                   GROUP BY mood 
                   ORDER BY count DESC""",
                (user_id,)
            ).fetchall()
            
            return {
                "total_journals": total,
                "mood_distribution": {row["mood"]: row["count"] for row in moods}
            }

    # ============================================================
    # 奖励系统
    # ============================================================

    def save_reward(self, user_id: str, reward_type: str, reward_name: str, xp_amount: int, badge_id: str = None, description: str = None) -> str:
        """保存奖励记录"""
        reward_id = f"reward_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO rewards 
                   (id, user_id, reward_type, reward_name, xp_amount, badge_id, description, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (reward_id, user_id, reward_type, reward_name, xp_amount, badge_id, description, now)
            )
        
        return reward_id

    def get_user_rewards(self, user_id: str, limit: int = 50) -> List[dict]:
        """获取用户的奖励记录"""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM rewards WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit)
            ).fetchall()
            return [dict(r) for r in rows]

    def award_badge(self, user_id: str, badge_id: str) -> bool:
        """授予用户徽章"""
        now = datetime.now().isoformat()
        
        with self._connect() as conn:
            # 检查是否已有徽章
            existing = conn.execute(
                "SELECT id FROM user_badges WHERE user_id = ? AND badge_id = ?",
                (user_id, badge_id)
            ).fetchone()
            
            if existing:
                return False  # 已有徽章
            
            # 授予徽章
            badge_user_id = f"badge_{uuid.uuid4().hex[:12]}"
            conn.execute(
                "INSERT INTO user_badges (id, user_id, badge_id, earned_at) VALUES (?, ?, ?, ?)",
                (badge_user_id, user_id, badge_id, now)
            )
            
            # 保存奖励记录
            badge = self.get_badge(badge_id)
            if badge:
                self.save_reward(
                    user_id=user_id,
                    reward_type="badge",
                    reward_name=f"获得徽章: {badge['name']}",
                    xp_amount=0,
                    badge_id=badge_id,
                    description=badge['description']
                )
            
            return True

    def has_badge(self, user_id: str, badge_id: str) -> bool:
        """检查用户是否有徽章"""
        with self._connect() as conn:
            result = conn.execute(
                "SELECT id FROM user_badges WHERE user_id = ? AND badge_id = ?",
                (user_id, badge_id)
            ).fetchone()
            return result is not None

    def get_user_badges(self, user_id: str) -> List[dict]:
        """获取用户的所有徽章"""
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT ub.*, b.name, b.description, b.icon 
                   FROM user_badges ub 
                   JOIN badges b ON ub.badge_id = b.id 
                   WHERE ub.user_id = ? 
                   ORDER BY ub.earned_at DESC""",
                (user_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_badge(self, badge_id: str) -> Optional[dict]:
        """获取徽章信息"""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM badges WHERE id = ?",
                (badge_id,)
            ).fetchone()
            return dict(row) if row else None

    def add_user_xp(self, user_id: str, xp_amount: int) -> bool:
        """增加用户经验值"""
        with self._connect() as conn:
            # 更新用户经验值
            cursor = conn.execute(
                "UPDATE users SET level = level + ? WHERE id = ?",
                (xp_amount, user_id)
            )
            return cursor.rowcount > 0

    def get_user_xp(self, user_id: str) -> int:
        """获取用户经验值"""
        with self._connect() as conn:
            result = conn.execute(
                "SELECT level FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()
            return result["level"] if result else 0

    def get_user_level(self, user_id: str) -> dict:
        """获取用户等级信息"""
        xp = self.get_user_xp(user_id)
        
        # 计算等级
        if xp < 100:
            level = 1
            title = "凡人"
        elif xp < 300:
            level = 2
            title = "看见者"
        elif xp < 600:
            level = 3
            title = "穿越者"
        elif xp < 1000:
            level = 4
            title = "觉醒者"
        else:
            level = 5
            title = "封神者"
        
        return {
            "level": level,
            "title": title,
            "xp": xp,
            "next_level_xp": level * 200,  # 每级需要200 XP
            "progress": (xp % 200) / 200 * 100  # 当前等级进度
        }

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
# 导出
# ============================================================

__all__ = ["Database"]
