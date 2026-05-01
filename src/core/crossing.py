"""
窄门 (NarrowGate) — 穿越训练引擎 (Crossing Engine)

核心哲学：每天做你最不想做的那件事。
不是舒适地成长，是在痛苦中重塑。

架构师：贾维斯 (Jarvis) for 小林医生
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from .gate_finder import NarrowGate


# ============================================================
# 数据模型
# ============================================================

@dataclass
class DailyChallenge:
    """每日挑战"""
    id: str
    gate_id: str
    date: str
    challenge: str
    difficulty: int  # 1-10
    status: str  # pending / in_progress / completed / skipped
    response: str = ""  # 用户完成后的反馈
    witness_verification: bool = False  # 是否有见证者验证
    completed_at: str = ""


@dataclass
class CrossingRecord:
    """穿越记录——你做了什么，结果如何"""
    id: str
    gate_id: str
    action: str  # 你做了什么
    fear_before: str  # 做之前害怕什么
    reality_after: str  # 做之后发现什么
    timestamp: str
    data_proof: str = ""  # 数据证据（截图/链接/第三方验证）
    emotional_state: str = ""  # 情绪状态


@dataclass
class CrossingProgress:
    """穿越进度追踪"""
    gate_id: str
    start_date: str
    current_day: int = 0
    total_days: int = 30
    challenges_completed: int = 0
    challenges_skipped: int = 0
    records: List[CrossingRecord] = field(default_factory=list)
    streak_days: int = 0  # 连续完成天数
    max_streak: int = 0

    @property
    def completion_rate(self) -> float:
        if self.current_day == 0:
            return 0
        return self.challenges_completed / self.current_day * 100

    @property
    def is_crossed(self) -> bool:
        """是否穿越了窄门"""
        return (
            self.current_day >= self.total_days
            and self.completion_rate >= 80
        )


# ============================================================
# 挑战生成器
# ============================================================

CHALLENGE_TEMPLATES = {
    "认知": {
        "舒适区依赖": [
            "今天用一个完全没用过的方法解决一个日常问题",
            "跟一个你通常不会交谈的人聊10分钟",
            "学一个你一直觉得'不适合自己'的技能的入门课",
            "读一篇你完全不同意其观点的文章，写3个它可能对的地方",
            "在会议上/群里主动提出一个你不确定的观点",
        ],
        "成功标准外包": [
            "写下你的成功定义，不参考任何人的标准",
            "放弃一个你在追求但不是你真正想要的目标",
            "对一个人说'我不想做这个，因为这不是我想要的'",
            "花30分钟做一件'没用但你开心'的事",
            "告诉一个人你真正的梦想，即使它听起来很荒谬",
        ],
    },
    "情绪": {
        "情绪压抑": [
            "今天允许自己在安全的环境里哭一次",
            "用文字写下你现在的真实感受，不修饰不美化",
            "对一个信任的人说'我现在很难过/愤怒/害怕'",
            "不要在别人问'你还好吗'时说'我很好'——说真话",
            "给你的一个情绪写一封信，告诉它你为什么一直压抑它",
        ],
        "羞耻回避": [
            "在朋友圈/社交媒体分享一次真实的失败经历",
            "告诉一个同事/朋友你最尴尬的一件事",
            "在被指出错误时说'你说得对'而不是辩解",
            "主动暴露一个你通常会隐藏的缺点",
            "写下你最羞耻的5个记忆，然后问自己：这真的那么糟吗？",
        ],
    },
    "行为": {
        "执行断裂": [
            "现在就做你拖延最久的那件事的前15分钟",
            "公开承诺今天要完成一件事，然后完成它",
            "设置一个25分钟计时器，只做那件你一直在逃避的事",
            "把你'明天再做'的清单里的一项挪到今天",
            "让一个人监督你今天完成一个具体任务",
        ],
        "多线程逃避": [
            "今天只做一件最重要的事，其他全部推后",
            "删掉手机上3个分散你注意力的App",
            "写下你的'不做清单'——至少列出5件你要停止做的事",
            "取消一个你其实不太想参加的安排",
            "把一个'也在做的项目'正式搁置，通知相关人员",
        ],
    },
    "关系": {
        "讨好模式": [
            "今天对一个你不真正想做的事说'不'",
            "在一个讨论中坚持你的立场，即使有人不高兴",
            "取消一个你只是为了维持关系而参加的聚会",
            "告诉一个人你对某事的真实看法，而不是他们想听的",
            "做一件让自己开心但'别人可能不理解'的事",
        ],
        "深度回避": [
            "对一个人完全坦诚一个你从未分享的想法",
            "在一段关系中主动表达脆弱而不是保持坚强",
            "问一个人一个你一直想问但不敢问的问题",
            "告诉一个亲近的人他们对你的真实影响（正面或负面）",
            "在被问'怎么了'时说出真正的问题，而不是'没事'",
        ],
    },
    "事业": {
        "野心恐惧": [
            "大声说出你真正的事业目标，即使它看起来'不现实'",
            "今天为那个'不可能的梦'做一件小事",
            "告诉一个你尊重的人你的真正野心",
            "写下5年后的理想状态，不设任何限制",
            "申请/报名一个你觉得'我不够格'的机会",
        ],
        "能力低估": [
            "今天开始做那个你觉得'还没准备好'的项目",
            "主动承担一个你觉得'超出能力'的任务",
            "让3个认识你的人给你写能力评价",
            "列出你过去做成的10件'你以为你做不到'的事",
            "在工作中主动展示一个你通常会藏起来的技能",
        ],
    },
}




# ============================================================
# 30天四周训练计划
# ============================================================

TRAINING_WEEKS = [
    {
        "week": 1,
        "name": "面对恐惧",
        "subtitle": "承认它存在，然后第一次尝试",
        "days": "D1-D7",
        "difficulty_range": "3-5",
        "color": "#ef4444",
        "focus": "建立行动感，突破表层回避",
        "principles": [
            "从最轻的不适开始",
            "每天只做一件事",
            "重点是'做了'而非'做好'",
        ],
    },
    {
        "week": 2,
        "name": "建立节奏",
        "subtitle": "每日挑战形成习惯回路",
        "days": "D8-D14",
        "difficulty_range": "5-7",
        "color": "#f97316",
        "focus": "建立每日穿越的稳定节奏",
        "principles": [
            "难度渐进提升",
            "引入见证人验证",
            "开始记录恐惧 vs 现实",
        ],
    },
    {
        "week": 3,
        "name": "突破瓶颈",
        "subtitle": "难度升级，直面核心恐惧",
        "days": "D15-D21",
        "difficulty_range": "7-8",
        "color": "#eab308",
        "focus": "突破核心恐惧，旧模式松动",
        "principles": [
            "直面你最不想面对的事",
            "公开暴露脆弱",
            "从被动挑战到主动穿越",
        ],
    },
    {
        "week": 4,
        "name": "巩固穿越",
        "subtitle": "从刻意到自然，内化新身份",
        "days": "D22-D30",
        "difficulty_range": "8-回顾",
        "color": "#c9a84c",
        "focus": "整合新身份，从玩家变导师",
        "principles": [
            "从Be到Do到Have",
            "帮助他人开始穿越",
            "写穿越旅程总结",
        ],
    },
]


def get_week_for_day(day: int) -> dict:
    """根据天数返回对应的周计划"""
    if day <= 7:
        return TRAINING_WEEKS[0]
    elif day <= 14:
        return TRAINING_WEEKS[1]
    elif day <= 21:
        return TRAINING_WEEKS[2]
    else:
        return TRAINING_WEEKS[3]


def get_training_plan() -> list:
    """返回完整30天训练计划"""
    return TRAINING_WEEKS

# ============================================================
# 穿越训练引擎
# ============================================================

class CrossingEngine:
    """
    穿越训练引擎

    职责：
    1. 生成每日挑战
    2. 追踪完成进度
    3. 收集穿越记录
    4. 判断是否穿越
    """

    def __init__(self):
        self.active_crossings: Dict[str, CrossingProgress] = {}

    def start_crossing(self, gate: NarrowGate) -> CrossingProgress:
        """开始穿越一个窄门"""
        progress = CrossingProgress(
            gate_id=gate.id,
            start_date=datetime.now().isoformat(),
            total_days=gate.estimated_crossing_days,
        )
        self.active_crossings[gate.id] = progress
        return progress

    def generate_daily_challenge(self, gate: NarrowGate, day: int) -> DailyChallenge:
        """
        生成今天的挑战

        策略：
        - 前10天：简单但持续（建立习惯）
        - 11-20天：中等难度（突破舒适区）
        - 21-30天：高难度（真正穿越）
        """
        dim = gate.dimension
        # 从名字中提取模板key
        gate_key = gate.name.split("：")[-1] if "：" in gate.name else gate.name

        templates = CHALLENGE_TEMPLATES.get(dim, {}).get(gate_key, [
            f"今天做一件你在{dim}方面最不想做的事",
            f"面对一个你在{dim}方面一直回避的真相",
            f"在{dim}方面公开暴露一个你的弱点",
        ])

        # 根据天数调整难度
        if day <= 10:
            difficulty = max(min(day, 5), 1)
        elif day <= 20:
            difficulty = min(day - 5, 7)
        else:
            difficulty = min(day - 10, 10)

        challenge_text = templates[day % len(templates)]

        return DailyChallenge(
            id=f"challenge_{gate.id}_day{day}",
            gate_id=gate.id,
            date=datetime.now().isoformat(),
            challenge=challenge_text,
            difficulty=difficulty,
            status="pending",
        )

    def record_challenge_completion(
        self,
        progress: CrossingProgress,
        challenge: DailyChallenge,
        response: str,
        witness: bool = False,
    ) -> CrossingRecord:
        """记录挑战完成"""
        challenge.status = "completed"
        challenge.response = response
        challenge.witness_verification = witness
        challenge.completed_at = datetime.now().isoformat()

        progress.current_day += 1
        progress.challenges_completed += 1
        progress.streak_days += 1
        progress.max_streak = max(progress.max_streak, progress.streak_days)

        record = CrossingRecord(
            id=f"record_{progress.gate_id}_day{progress.current_day}",
            gate_id=progress.gate_id,
            action=challenge.challenge,
            fear_before="待填写",
            reality_after=response,
            timestamp=datetime.now().isoformat(),
        )
        progress.records.append(record)

        return record

    def skip_challenge(self, progress: CrossingProgress, reason: str):
        """跳过今天的挑战"""
        progress.current_day += 1
        progress.challenges_skipped += 1
        progress.streak_days = 0  # 断签

    def get_progress_report(self, progress: CrossingProgress) -> dict:
        """生成进度报告"""
        return {
            "gate_id": progress.gate_id,
            "days_elapsed": progress.current_day,
            "total_days": progress.total_days,
            "completion_rate": f"{progress.completion_rate:.1f}%",
            "streak": progress.streak_days,
            "max_streak": progress.max_streak,
            "completed": progress.challenges_completed,
            "skipped": progress.challenges_skipped,
            "is_crossed": progress.is_crossed,
            "remaining": progress.total_days - progress.current_day,
            "message": self._generate_progress_message(progress),
        }

    def _generate_progress_message(self, progress: CrossingProgress) -> str:
        """生成进度消息"""
        if progress.is_crossed:
            return (
                "🚪 你穿越了窄门。\n\n"
                f"{progress.total_days}天，{progress.challenges_completed}次挑战完成。\n"
                f"完成率：{progress.completion_rate:.0f}%\n"
                f"最长连续：{progress.max_streak}天\n\n"
                "你已经不是开始时的那个人了。\n"
                "欢迎来到看见层。"
            )

        rate = progress.completion_rate
        if rate >= 80:
            status = "🔥 你在穿越的路上。继续保持。"
        elif rate >= 50:
            status = "⚡ 你走走停停。窄门需要坚持。"
        elif rate >= 20:
            status = "⚠️ 你在宽门和窄门之间犹豫。选择一个。"
        else:
            status = "🚪 你还在宽门上。窄门在等你，但它不会等太久。"

        return (
            f"{status}\n\n"
            f"进度：{progress.current_day}/{progress.total_days}天\n"
            f"完成率：{rate:.0f}%\n"
            f"连续：{progress.streak_days}天"
        )


# ============================================================
# 导出
# ============================================================

__all__ = [
    "CrossingEngine",
    "DailyChallenge",
    "CrossingRecord",
    "CrossingProgress",
    "CHALLENGE_TEMPLATES",
]
