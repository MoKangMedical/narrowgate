"""
窄门 (NarrowGate) — 进化金字塔 (Evolution Pyramid)

核心哲学：灵魂的进化不是线性的，是螺旋上升的。
每个层级都有不同的风景，也有不同的窄门。

架构师：贾维斯 (Jarvis) for 小林医生
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field


# ============================================================
# 五层进化金字塔
# ============================================================

EVOLUTION_LEVELS = [
    {
        "level": 1,
        "name": "睡眠层 (Sleep)",
        "emoji": "😴",
        "description": "大多数人所在的地方。你的枷锁驱动你的行为，但你不知道。你以为你的选择是自由的，但它们是枷锁的自动反应。",
        "characteristics": [
            "认为'我就是这样的人'",
            "不觉得有什么需要改变",
            "把问题归因于外部",
            "舒适区就是整个世界",
        ],
        "transition_sign": "当你开始怀疑'也许问题在我'的时候，你就在走向觉醒。",
        "color": "#374151",
    },
    {
        "level": 2,
        "name": "觉醒层 (Awakening)",
        "emoji": "👁️",
        "description": "你开始看到自己的枷锁。不等于解决——但至少看见了。这个阶段会带来不适和焦虑，因为你发现'我'是一个需要修理的东西。",
        "characteristics": [
            "开始问'为什么我总是这样'",
            "对自己行为的模式有觉察",
            "感到不适和焦虑",
            "想要改变但不知道如何",
        ],
        "transition_sign": "当你开始用行动而不是觉察来回应时，你就在走向突破。",
        "color": "#7c3aed",
    },
    {
        "level": 3,
        "name": "突破层 (Breakthrough)",
        "emoji": "⚡",
        "description": "你第一次穿越了窄门。不是'我想改变'——是你实际做了你最不想做的事。这个突破证明了你可以改变。",
        "characteristics": [
            "完成了一次穿越挑战",
            "体验到'另一种可能'",
            "开始建立新习惯",
            "旧模式开始松动",
        ],
        "transition_sign": "当突破从一次性的事件变成稳定的习惯时，你就在走向精通。",
        "color": "#c9a84c",
    },
    {
        "level": 4,
        "name": "精通层 (Mastery)",
        "emoji": "🎯",
        "description": "穿越成为习惯。你的窄门不再是'我能不能'——而是'我想不想'。你开始看到更深层的枷锁。",
        "characteristics": [
            "穿越窄门成为自然",
            "能够指导他人穿越",
            "看到更深层的枷锁",
            "稳定的新模式",
        ],
        "transition_sign": "当你不再需要刻意穿越——当窄门变成你的路时——你就在走向神性。",
        "color": "#dc2626",
    },
    {
        "level": 5,
        "name": "神性层 (Divinity)",
        "emoji": "✨",
        "description": "你不再是'你在穿越窄门'——窄门就是你的路。你的存在本身就是一种穿越。这是最高的层级。",
        "characteristics": [
            "窄门成为常态",
            "不再需要刻意努力",
            "存在即穿越",
            "你的光芒照亮他人的窄门",
        ],
        "transition_sign": "你已经不需要证明了。",
        "color": "#fbbf24",
    },
]


@dataclass
class EvolutionState:
    """进化状态"""
    current_level: int = 1
    experience_points: int = 0
    breakthroughs: List[Dict] = field(default_factory=list)  # 突破记录
    milestones: List[str] = field(default_factory=list)  # 里程碑

    @property
    def level_data(self) -> dict:
        return EVOLUTION_LEVELS[min(self.current_level - 1, 4)]

    @property
    def next_level_data(self) -> Optional[dict]:
        if self.current_level < 5:
            return EVOLUTION_LEVELS[self.current_level]
        return None

    @property
    def progress_to_next(self) -> float:
        """到下一级的进度 (0-100)"""
        thresholds = [0, 100, 300, 600, 1000]
        if self.current_level >= 5:
            return 100
        threshold = thresholds[self.current_level]
        if threshold == 0:
            return 100
        return min(100, self.experience_points / threshold * 100)

    def add_experience(self, points: int, source: str = ""):
        """添加经验"""
        self.experience_points += points
        self._check_level_up()

    def _check_level_up(self):
        """检查是否升级"""
        thresholds = [0, 100, 300, 600, 1000]
        while self.current_level < 5:
            if self.experience_points >= thresholds[self.current_level]:
                self.current_level += 1
                self.milestones.append(
                    f"进化至第{self.current_level}层：{EVOLUTION_LEVELS[self.current_level-1]['name']}"
                )
            else:
                break


# ============================================================
# 进化金字塔引擎
# ============================================================

class EvolutionPyramid:
    """
    进化金字塔

    职责：
    1. 管理进化状态
    2. 记录突破
    3. 生成进化报告
    4. 提供可视化数据
    """

    def __init__(self):
        self._states: Dict[str, EvolutionState] = {}

    def get_state(self, user_id: str) -> EvolutionState:
        """获取用户进化状态"""
        if user_id not in self._states:
            self._states[user_id] = EvolutionState()
        return self._states[user_id]

    def record_breakthrough(self, user_id: str, gate_name: str, description: str) -> dict:
        """记录突破"""
        state = self.get_state(user_id)
        state.add_experience(50, "breakthrough")

        breakthrough = {
            "gate": gate_name,
            "description": description,
            "level_at_time": state.current_level,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }
        state.breakthroughs.append(breakthrough)

        return breakthrough

    def record_crossing_completion(self, user_id: str, gate_name: str) -> dict:
        """记录穿越完成"""
        state = self.get_state(user_id)
        old_level = state.current_level
        state.add_experience(200, "crossing_complete")

        result = {
            "experience_gained": 200,
            "total_experience": state.experience_points,
            "current_level": state.current_level,
            "level_up": state.current_level > old_level,
        }

        if result["level_up"]:
            level_data = EVOLUTION_LEVELS[state.current_level - 1]
            result["new_level_name"] = level_data["name"]
            result["new_level_emoji"] = level_data["emoji"]

        return result

    def record_daily_challenge(self, user_id: str) -> dict:
        """记录每日挑战完成"""
        state = self.get_state(user_id)
        old_level = state.current_level
        state.add_experience(10, "daily_challenge")

        return {
            "experience_gained": 10,
            "total_experience": state.experience_points,
            "current_level": state.current_level,
            "level_up": state.current_level > old_level,
        }

    def get_pyramid_data(self, user_id: str) -> dict:
        """获取金字塔可视化数据"""
        state = self.get_state(user_id)

        levels = []
        for level in EVOLUTION_LEVELS:
            level_data = {
                "level": level["level"],
                "name": level["name"],
                "emoji": level["emoji"],
                "description": level["description"],
                "color": level["color"],
                "characteristics": level["characteristics"],
                "is_current": level["level"] == state.current_level,
                "is_reached": level["level"] <= state.current_level,
            }
            levels.append(level_data)

        return {
            "levels": levels,
            "current_level": state.current_level,
            "experience_points": state.experience_points,
            "progress_to_next": state.progress_to_next,
            "breakthroughs": len(state.breakthroughs),
            "milestones": state.milestones,
            "next_transition": (
                EVOLUTION_LEVELS[state.current_level - 1].get("transition_sign", "")
                if state.current_level <= 5 else ""
            ),
        }

    def get_visual_pyramid(self, user_id: str) -> str:
        """获取ASCII金字塔可视化"""
        state = self.get_state(user_id)

        lines = [
            "          ✨          ",
            "        ┌───┐        ",
            "        │ 5 │        " if state.current_level >= 5 else "        │ · │        ",
            "      ┌─┴───┴─┐      ",
            "      │   4   │      " if state.current_level >= 4 else "      │   ·   │      ",
            "    ┌─┴───────┴─┐    ",
            "    │     3     │    " if state.current_level >= 3 else "    │     ·     │    ",
            "  ┌─┴───────────┴─┐  ",
            "  │      2        │  " if state.current_level >= 2 else "  │      ·        │  ",
            "┌─┴───────────────┴─┐",
            "│        1          │",
            "└───────────────────┘",
        ]

        return "\n".join(lines)


# ============================================================
# 导出
# ============================================================

__all__ = [
    "EvolutionPyramid",
    "EvolutionState",
    "EVOLUTION_LEVELS",
]
