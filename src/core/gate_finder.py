"""
窄门 (NarrowGate) — 窄门识别器 (Gate Finder)

核心算法：痛苦回避度 × 成长杠杆率 = 窄门优先级
你最不想面对的 × 能带来最大改变的 = 你最需要穿越的

架构师：贾维斯 (Jarvis) for 小林医生
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from .soul_audit import Shackle, SoulAudit


# ============================================================
# 数据模型
# ============================================================

@dataclass
class NarrowGate:
    """一个具体的窄门——你需要穿越的困境"""
    id: str
    name: str
    description: str
    dimension: str
    priority_score: float  # 0-100

    # 为什么这是你的窄门
    why_this_gate: str

    # 宽门 vs 窄门
    wide_gate_path: str  # 多数人走的路（容易但无效）
    narrow_gate_path: str  # 你该走的路（难但有效）

    # 穿越指标
    crossing_indicators: List[str] = field(default_factory=list)
    # 怎么知道自己穿越了

    # 关联的枷锁
    source_shackles: List[str] = field(default_factory=list)

    # 预估穿越时间
    estimated_crossing_days: int = 30

    # 每日挑战模板
    daily_challenge_template: str = ""


@dataclass
class GatePath:
    """穿越窄门的路径规划"""
    gate_id: str
    phases: List[Dict] = field(default_factory=list)
    # 每个阶段: {"name": "xxx", "days": 7, "challenges": [...]}


# ============================================================
# 窄门知识库
# ============================================================

GATE_TEMPLATES = {
    "认知": {
        "舒适区依赖": {
            "description": "你一直在用已知的方式做事，回避未知领域",
            "wide_gate": "做你擅长的事，避开不擅长的",
            "narrow_gate": "每周做一件你完全不擅长的事，公开记录",
            "indicators": ["连续30天尝试新事物", "公开承认三次失败", "有人指出你变了"],
            "daily_challenge": "今天做一件让你感到'我不确定我能做好'的事",
        },
        "成功标准外包": {
            "description": "你用别人的标准定义自己的成功",
            "wide_gate": "追求社会认可的成就（好工作/好房子/好车）",
            "narrow_gate": "写下你真正想要的，即使它不符合任何人的期待",
            "indicators": ["能清晰说出自己的成功定义", "放弃了至少一个别人的期待", "感到焦虑但不后悔"],
            "daily_challenge": "今天做一件'没人会认可但你觉得对'的事",
        },
    },
    "情绪": {
        "情绪压抑": {
            "description": "你把情绪当作敌人，压制一切不舒服的感受",
            "wide_gate": "控制情绪，保持冷静，做理性的人",
            "narrow_gate": "允许自己感受每一种情绪，不评判，不压制",
            "indicators": ["能在人前哭", "能说'我很愤怒'而不是'我很好'", "不再用忙碌逃避感受"],
            "daily_challenge": "今天找一个安全的人，说出一个你从未表达的真实感受",
        },
        "羞耻回避": {
            "description": "你被羞耻感驱动，做很多事只是为了不感到羞耻",
            "wide_gate": "确保自己不犯错，不被嘲笑，不丢脸",
            "narrow_gate": "主动暴露自己的不完美，让羞耻感失去力量",
            "indicators": ["公开分享一个失败经历", "被嘲笑后不防御", "不再隐藏自己的弱点"],
            "daily_challenge": "今天告诉一个人你最尴尬的一件事",
        },
    },
    "行为": {
        "执行断裂": {
            "description": "你知道该做什么，但就是不做",
            "wide_gate": "等准备好了再开始，找最佳时机",
            "narrow_gate": "现在就做最烂的第一版，不等准备好",
            "indicators": ["连续30天执行同一个计划", "公开承诺并完成", "不再找借口"],
            "daily_challenge": "今天完成你拖延最久的那件事的前10分钟",
        },
        "多线程逃避": {
            "description": "你同时做很多事，这样每件事做不好都有借口",
            "wide_gate": "什么都尝试，保持选择开放",
            "narrow_gate": "砍掉一切，只留一个方向，做到极致",
            "indicators": ["砍掉了至少3个'也在做'的事", "连续90天专注一件事", "有人说你'变专注了'"],
            "daily_challenge": "今天列一个'不做清单'，砍掉5件分散精力的事",
        },
    },
    "关系": {
        "讨好模式": {
            "description": "你通过满足别人来获得安全感",
            "wide_gate": "让所有人都喜欢你，不得罪任何人",
            "narrow_gate": "对一个人说一次真正的'不'，承受关系紧张",
            "indicators": ["拒绝了一个重要的人", "关系没有因此破裂", "感到内疚但不后悔"],
            "daily_challenge": "今天对一个你不真正想做的事说'不'",
        },
        "深度回避": {
            "description": "你维持表面关系，回避真正的亲密",
            "wide_gate": "保持友好但有距离的关系",
            "narrow_gate": "对一个人完全坦诚，包括你的恐惧和弱点",
            "indicators": ["有人知道你最深的秘密", "能在关系中感到脆弱", "不再表演完美"],
            "daily_challenge": "今天告诉一个人一个你从未说过的真实想法",
        },
    },
    "事业": {
        "野心恐惧": {
            "description": "你有真正想要的，但不敢承认，因为承认了就要面对可能的失败",
            "wide_gate": "设定'现实'的目标，避免失望",
            "narrow_gate": "大声说出你真正想要的，即使它看起来不可能",
            "indicators": ["公开宣告一个'不现实'的目标", "为之行动了30天", "不再为自己有野心而道歉"],
            "daily_challenge": "今天写下你真正想要的事业目标，不修饰，不打折扣",
        },
        "能力低估": {
            "description": "你比自己认为的更有能力，但你在用'还不够好'来逃避",
            "wide_gate": "继续学习，继续准备，等'真正准备好'再开始",
            "narrow_gate": "今天就开始做那个你以为'还不够格'的事",
            "indicators": ["做了一件'超出能力'的事", "结果比预期好", "不再用准备当借口"],
            "daily_challenge": "今天申请/开始/报名一个你觉得'我还不够格'的机会",
        },
    },
}


# ============================================================
# 窄门识别引擎
# ============================================================

class GateFinder:
    """
    窄门识别器

    从灵魂审计的结果中，识别出用户当前最需要穿越的窄门。
    """

    def __init__(self):
        self.gate_templates = GATE_TEMPLATES

    def find_gates(self, audit: SoulAudit) -> List[NarrowGate]:
        """
        从审计结果中识别窄门

        Returns: 按优先级排序的窄门列表
        """
        gates = []

        for shackle_id, shackle in audit.shackle_map.items():
            # 匹配窄门模板
            gate = self._match_gate_template(shackle)
            if gate:
                gate.source_shackles.append(shackle_id)
                gates.append(gate)

        # 按优先级排序
        gates.sort(key=lambda g: g.priority_score, reverse=True)

        return gates

    def _match_gate_template(self, shackle: Shackle) -> Optional[NarrowGate]:
        """将枷锁匹配到窄门模板"""
        dim_templates = self.gate_templates.get(shackle.dimension, {})

        best_match = None
        best_score = 0

        for gate_name, template in dim_templates.items():
            # 简单的关键词匹配（实际应用中可用语义匹配）
            score = 0
            desc_words = set(template["description"])
            shackle_words = set(shackle.description + shackle.name)

            # 维度匹配得基础分
            score += 20

            # 回避度加权
            score += shackle.evasion_level * 0.3

            # 深度加权
            score += shackle.depth_score * 0.3

            if score > best_score:
                best_score = score
                best_match = (gate_name, template)

        if best_match:
            name, template = best_match
            return NarrowGate(
                id=f"gate_{shackle.dimension}_{name}",
                name=f"{shackle.dimension}：{name}",
                description=template["description"],
                dimension=shackle.dimension,
                priority_score=shackle.gate_priority,
                why_this_gate=f"你在{shackle.dimension}维度反复出现回避，这不只是一个问题，这是你当前最大的成长瓶颈。",
                wide_gate_path=template["wide_gate"],
                narrow_gate_path=template["narrow_gate"],
                crossing_indicators=template["indicators"],
                daily_challenge_template=template["daily_challenge"],
            )

        return None

    def generate_gate_report(self, gates: List[NarrowGate]) -> dict:
        """生成窄门报告"""
        if not gates:
            return {
                "status": "no_gates_found",
                "message": "没有找到明显的窄门。这可能意味着你已经很自洽，或者需要更深入的审计。",
            }

        primary_gate = gates[0]

        return {
            "status": "gates_found",
            "primary_gate": {
                "name": primary_gate.name,
                "description": primary_gate.description,
                "why": primary_gate.why_this_gate,
                "wide_vs_narrow": {
                    "wide_gate": primary_gate.wide_gate_path,
                    "narrow_gate": primary_gate.narrow_gate_path,
                },
                "crossing_signs": primary_gate.crossing_indicators,
                "daily_challenge": primary_gate.daily_challenge_template,
                "estimated_days": primary_gate.estimated_crossing_days,
            },
            "other_gates": [
                {"name": g.name, "priority": g.priority_score}
                for g in gates[1:3]
            ],
            "message": (
                f"你的窄门已经显现：**{primary_gate.name}**\n\n"
                f"宽门路径：{primary_gate.wide_gate_path}\n"
                f" → 多数人走这条路，容易，但你永远在原地\n\n"
                f"窄门路径：{primary_gate.narrow_gate_path}\n"
                f" → 难，痛苦，但穿越后你不再是从前的你\n\n"
                f"穿越标准：\n"
                + "\n".join(f"  ✓ {ind}" for ind in primary_gate.crossing_indicators)
                + f"\n\n今天的挑战：{primary_gate.daily_challenge_template}"
            ),
        }


# ============================================================
# 导出
# ============================================================

__all__ = [
    "GateFinder",
    "NarrowGate",
    "GatePath",
    "GATE_TEMPLATES",
]
