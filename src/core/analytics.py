"""
窄门 (NarrowGate) - 数据分析模块

用户行为追踪、统计分析
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from core.logger import get_logger

logger = get_logger("analytics")


class AnalyticsManager:
    """数据分析管理器"""
    
    def __init__(self, db):
        self.db = db
        self._init_analytics_tables()
    
    def _init_analytics_tables(self):
        """初始化分析表"""
        with self.db._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS user_events (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_data TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_events_user ON user_events(user_id);
                CREATE INDEX IF NOT EXISTS idx_events_type ON user_events(event_type);
                CREATE INDEX IF NOT EXISTS idx_events_time ON user_events(created_at);
            """)
    
    def track_event(self, user_id: str, event_type: str, event_data: Dict = None):
        """追踪用户事件"""
        event_id = f"event_{uuid.uuid4().hex[:12]}"
        
        with self.db._connect() as conn:
            conn.execute(
                """INSERT INTO user_events (id, user_id, event_type, event_data)
                VALUES (?, ?, ?, ?)""",
                (event_id, user_id, event_type, json.dumps(event_data or {}))
            )
        
        logger.debug(f"📊 事件追踪: {user_id} - {event_type}")
    
    def get_daily_active_users(self, date: str = None) -> int:
        """获取日活跃用户数"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        with self.db._connect() as conn:
            result = conn.execute(
                """SELECT COUNT(DISTINCT user_id) 
                FROM user_events 
                WHERE DATE(created_at) = ?""",
                (date,)
            ).fetchone()
            
            return result[0] if result else 0
    
    def get_monthly_active_users(self, year: int = None, month: int = None) -> int:
        """获取月活跃用户数"""
        if not year or not month:
            now = datetime.now()
            year = now.year
            month = now.month
        
        with self.db._connect() as conn:
            result = conn.execute(
                """SELECT COUNT(DISTINCT user_id) 
                FROM user_events 
                WHERE strftime('%Y', created_at) = ? 
                AND strftime('%m', created_at) = ?""",
                (str(year), str(month).zfill(2))
            ).fetchone()
            
            return result[0] if result else 0
    
    def get_popular_features(self, days: int = 7) -> List[Dict]:
        """获取热门功能"""
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        with self.db._connect() as conn:
            results = conn.execute(
                """SELECT event_type, COUNT(*) as count, COUNT(DISTINCT user_id) as users
                FROM user_events 
                WHERE DATE(created_at) >= ?
                GROUP BY event_type
                ORDER BY count DESC""",
                (start_date,)
            ).fetchall()
            
            return [
                {
                    "event_type": row['event_type'],
                    "total_count": row['count'],
                    "unique_users": row['users']
                }
                for row in results
            ]
    
    def get_dashboard_data(self) -> Dict:
        """获取仪表板数据"""
        return {
            "dau": self.get_daily_active_users(),
            "mau": self.get_monthly_active_users(),
            "popular_features": self.get_popular_features(7)
        }


def create_analytics_routes(app, analytics_manager: AnalyticsManager):
    """创建分析API路由"""
    from fastapi import Request
    
    @app.post("/api/analytics/event")
    async def track_event(request: Request):
        """追踪事件"""
        data = await request.json()
        user_id = data.get('user_id')
        event_type = data.get('event_type')
        event_data = data.get('event_data', {})
        
        if not user_id or not event_type:
            return {"error": "缺少必要参数"}
        
        analytics_manager.track_event(user_id, event_type, event_data)
        return {"success": True}
    
    @app.get("/api/analytics/dashboard")
    async def get_dashboard():
        """获取仪表板数据"""
        return analytics_manager.get_dashboard_data()
    
    return analytics_manager