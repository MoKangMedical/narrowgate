"""
窄门 (NarrowGate) — 灵魂审计引擎 (Soul Audit Engine)

核心哲学：不接受表面答案，持续追问直到真相浮现。
这是鉴别诊断思维在个人成长领域的应用。

架构师：贾维斯 (Jarvis) for 小林医生
"""

import json
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict


# ============================================================
# 数据模型
# ============================================================

@dataclass
class Shackle:
    """枷锁：一个具体的、被识别的自我限制模式"""
    id: str
    name: str
    description: str
    dimension: str  # 认知/情绪/行为/关系/事业
    depth_score: float  # 0-100, 越高越根深蒂固
    evasion_level: float  # 0-100, 你有多回避面对它
    evidence: List[str] = field(default_factory=list)
    first_seen: str = ""
    last_updated: str = ""

    def __post_init__(self):
        if not self.first_seen:
            self.first_seen = datetime.now().isoformat()
        self.last_updated = datetime.now().isoformat()

    @property
    def gate_priority(self) -> float:
        """
        窄门优先级 = 回避度 × 根深度
        你最不想面对的 × 最根深蒂固的 = 你最需要穿越的
        """
        return self.evasion_level * self.depth_score / 100


@dataclass
class AuditQuestion:
    """审计追问：AI生成的深度问题"""
    question: str
    dimension: str
    depth_level: int  # 1=表面, 2=中层, 3=深层, 4=核心
    purpose: str  # 这个问题要挖什么
    expected_evasion: str  # 预期的回避模式


@dataclass
class AuditResponse:
    """用户的审计回答"""
    question: str
    answer: str
    timestamp: str
    depth_level: int
    dimension: str = ""  # 所属维度
    evasion_detected: bool = False
    evasion_type: str = ""  # 否认/转移/最小化/合理化/攻击
    ai_analysis: str = ""


@dataclass
class SoulAudit:
    """完整的灵魂审计"""
    id: str
    user_id: str
    status: str  # in_progress / completed / archived
    current_dimension: str
    current_depth: int
    shackle_map: Dict[str, Shackle] = field(default_factory=dict)
    conversation: List[AuditResponse] = field(default_factory=list)
    gate_candidates: List[str] = field(default_factory=list)  # 窄门候选 ID
    started_at: str = ""
    completed_at: str = ""

    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.now().isoformat()

    @property
    def top_gates(self) -> List[Shackle]:
        """返回优先级最高的窄门候选"""
        shackles = [self.shackle_map[sid] for sid in self.gate_candidates if sid in self.shackle_map]
        return sorted(shackles, key=lambda s: s.gate_priority, reverse=True)[:3]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status,
            "shackle_count": len(self.shackle_map),
            "top_gates": [
                {"name": s.name, "priority": s.gate_priority, "dimension": s.dimension}
                for s in self.top_gates
            ],
            "conversation_length": len(self.conversation),
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


# ============================================================
# 审计维度与追问模板
# ============================================================

AUDIT_DIMENSIONS = {
    "认知": {
        "description": "你的思维模式、信念系统、世界观",
        "surface_questions": [
            "你觉得自己的人生到现在，最大的成就是什么？",
            "你认为成功最重要的因素是什么？",
            "你最近一次改变一个长期持有的观点是什么时候？",
        ],
        "evasion_patterns": ["宏大叙事回避细节", "用别人的标准定义成功", "把运气当能力"],
    },
    "情绪": {
        "description": "你如何感受、表达、压抑情绪",
        "surface_questions": [
            "你上一次真正生气是什么时候？因为什么？",
            "什么事情会让你感到羞耻？",
            "你最害怕别人发现你什么？",
        ],
        "evasion_patterns": ["我不太有情绪", "都过去了", "别人都这样"],
    },
    "行为": {
        "description": "你的习惯、执行力、自律模式",
        "surface_questions": [
            "你明知道应该做但一直没做的事情是什么？",
            "你每天花时间最多的事情是什么？",
            "你上次为一个目标坚持超过三个月是什么时候？",
        ],
        "evasion_patterns": ["太忙了", "还没准备好", "条件不允许"],
    },
    "关系": {
        "description": "你与他人的连接模式、边界、依赖",
        "surface_questions": [
            "你最亲近的人，你觉得他们真正了解你吗？",
            "你有没有维持着一段让你不舒服但不敢结束的关系？",
            "你帮过别人最大的忙是什么？你为什么帮？",
        ],
        "evasion_patterns": ["我人缘挺好的", "都是别人的问题", "我不需要别人"],
    },
    "事业": {
        "description": "你的野心、恐惧、能力与现实的差距",
        "surface_questions": [
            "如果没有任何限制，你真正想做什么？",
            "你觉得自己现在配得上自己想要的位置吗？",
            "你有没有在用\"还没准备好\"来逃避一个你其实可以开始的事情？",
        ],
        "evasion_patterns": ["现实就是这样", "时机不对", "我不是那种人"],
    },
}


# ============================================================
# 回避检测器
# ============================================================

EVASION_SIGNALS = {
    "否认": [
        "没有", "不是", "我不觉得", "还好", "还行", "正常",
        "没什么特别", "都一样", "无所谓",
    ],
    "转移": [
        "说起来", "对了", "另外", "其实我想说", "换个角度",
        "更关键的是", "这个不重要",
    ],
    "最小化": [
        "一点点", "稍微", "可能有一点", "还好吧", "不算什么",
        "小事", "问题不大",
    ],
    "合理化": [
        "因为", "所以", "没办法", "大家都这样", "这是正常的",
        "换谁都会", "没办法的事", "情有可原",
    ],
    "攻击": [
        "你问这个干嘛", "这有什么意义", "你不理解",
        "这问题不对", "太简单了",
    ],
}


def detect_evasion(answer: str) -> tuple[bool, str]:
    """
    检测回答中的回避模式

    Returns: (是否检测到回避, 回避类型)
    """
    answer_lower = answer.lower().strip()

    # 极短回答可能在回避
    if len(answer_lower) < 10:
        return True, "回避—过短回答"

    for evasion_type, signals in EVASION_SIGNALS.items():
        for signal in signals:
            if signal in answer_lower:
                return True, evasion_type

    return False, ""


# ============================================================
# 灵魂审计引擎
# ============================================================

class SoulAuditEngine:
    """
    灵魂审计引擎

    核心职责：
    1. 驱动深度对话，逐层剥开表象
    2. 检测回避模式，不接受表面答案
    3. 识别和记录枷锁
    4. 生成窄门候选
    """

    def __init__(self, mimo_api_key: str = "", mimo_base_url: str = ""):
        self.mimo_api_key = mimo_api_key
        self.mimo_base_url = mimo_base_url
        self.active_audits: Dict[str, SoulAudit] = {}

    def create_audit(self, user_id: str) -> SoulAudit:
        """创建新的灵魂审计"""
        audit_id = f"audit_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        audit = SoulAudit(
            id=audit_id,
            user_id=user_id,
            status="in_progress",
            current_dimension="认知",
            current_depth=1,
        )
        self.active_audits[audit_id] = audit
        return audit

    def get_next_question(self, audit: SoulAudit) -> AuditQuestion:
        """
        生成下一个追问

        策略：
        1. 表层问题 (depth=1)：开放式探索
        2. 中层追问 (depth=2)：针对回答中的矛盾
        3. 深层追问 (depth=3)：指向回避模式
        4. 核心直击 (depth=4)：剥离所有伪装
        """
        dimension = audit.current_dimension
        dim_info = AUDIT_DIMENSIONS[dimension]
        depth = audit.current_depth

        if depth == 1:
            # 表面探索
            question = dim_info["surface_questions"][
                len([c for c in audit.conversation if c.depth_level == 1])
                % len(dim_info["surface_questions"])
            ]
            return AuditQuestion(
                question=question,
                dimension=dimension,
                depth_level=1,
                purpose="探索表层认知",
                expected_evasion="标准化答案",
            )

        elif depth == 2:
            # 中层追问：指向矛盾
            last_response = audit.conversation[-1] if audit.conversation else None
            if last_response and last_response.evasion_detected:
                question = f"你刚才说\"{last_response.answer[:30]}...\"，但我想知道的是——在这背后，你真正害怕面对的是什么？"
            else:
                question = f"在{dimension}这个维度上，你觉得自己的最大短板是什么？为什么到现在还没解决？"
            return AuditQuestion(
                question=question,
                dimension=dimension,
                depth_level=2,
                purpose="指向回避和矛盾",
                expected_evasion="更深的合理化",
            )

        elif depth == 3:
            # 深层追问：直击痛点
            question = f"如果让你在{dimension}方面对自己做一个残酷的诚实评价，满分10分你给自己打几分？扣掉的分丢在哪里了？"
            return AuditQuestion(
                question=question,
                dimension=dimension,
                depth_level=3,
                purpose="强迫量化自我评价",
                expected_evasion="模糊化/转移",
            )

        else:
            # 核心直击
            question = f"最后一个问题：在{dimension}方面，你有没有一个从未告诉任何人的秘密？关于你是谁、你做过什么、或者你真正想要什么？"
            return AuditQuestion(
                question=question,
                dimension=dimension,
                depth_level=4,
                purpose="击穿所有防御机制",
                expected_evasion="强烈抵抗或突破",
            )

    def process_response(self, audit: SoulAudit, answer: str) -> AuditResponse:
        """
        处理用户回答

        Returns: 审计响应（包含回避检测结果和AI分析）
        """
        # 检测回避
        evasion_detected, evasion_type = detect_evasion(answer)

        # 构建响应
        response = AuditResponse(
            question=self.get_next_question(audit).question,
            answer=answer,
            timestamp=datetime.now().isoformat(),
            depth_level=audit.current_depth,
            dimension=audit.current_dimension,
            evasion_detected=evasion_detected,
            evasion_type=evasion_type,
        )

        # 如果检测到回避，生成分析
        if evasion_detected:
            response.ai_analysis = self._generate_evasion_analysis(audit, answer, evasion_type)

        # 记录对话
        audit.conversation.append(response)

        # 更新深度
        if evasion_detected:
            # 检测到回避 = 这里有枷锁，继续深挖
            audit.current_depth = min(audit.current_depth + 1, 4)
        else:
            # 没有回避 = 这个维度可能已经到底了，切换维度
            if audit.current_depth >= 3:
                self._switch_dimension(audit)
            else:
                audit.current_depth += 1

        # 尝试识别枷锁
        self._try_identify_shackle(audit, response)

        return response

    def _generate_evasion_analysis(
        self, audit: SoulAudit, answer: str, evasion_type: str
    ) -> str:
        """生成回避分析"""
        analyses = {
            "否认": "你在否认。这很正常——人的大脑会自动过滤威胁性信息。但我需要你说出那个你不想承认的东西。",
            "转移": "你在转移话题。这意味着刚才的问题触碰到了某个敏感区域。让我们回到那个点。",
            "最小化": "你在最小化。'一点点'、'还好'——这些词是在给自己的回避找台阶。真实感受是什么？",
            "合理化": "你在合理化。每个'因为'后面都藏着一个真正的恐惧。抛开理由，你的直觉告诉你什么？",
            "攻击": "你在攻击问题本身。这意味着问题击中了要害。我不会退让——回答它。",
        }
        return analyses.get(evasion_type, "我感觉到你在回避。没关系，但我们需要再试一次。")

    def _switch_dimension(self, audit: SoulAudit):
        """切换到下一个审计维度"""
        dimensions = list(AUDIT_DIMENSIONS.keys())
        current_idx = dimensions.index(audit.current_dimension)
        next_idx = (current_idx + 1) % len(dimensions)
        audit.current_dimension = dimensions[next_idx]
        audit.current_depth = 1

    def _try_identify_shackle(self, audit: SoulAudit, response: AuditResponse):
        """尝试从对话中识别枷锁"""
        if not response.evasion_detected:
            return

        # 如果同一维度深度3+且反复回避，这里很可能有枷锁
        same_dim_evasions = [
            r for r in audit.conversation
            if r.dimension == audit.current_dimension and r.evasion_detected  # noqa
        ]

        if len(same_dim_evasions) >= 2:
            # 生成枷锁
            shackle_id = f"shackle_{audit.current_dimension}_{len(audit.shackle_map)}"
            shackle = Shackle(
                id=shackle_id,
                name=f"{audit.current_dimension}回避模式 #{len(audit.shackle_map) + 1}",
                description=f"在{audit.current_dimension}维度反复出现{response.evasion_type}回避",
                dimension=audit.current_dimension,
                depth_score=min(len(same_dim_evasions) * 25, 100),
                evasion_level=80,  # 反复回避 = 高回避度
                evidence=[r.answer[:50] for r in same_dim_evasions[-3:]],
            )
            audit.shackle_map[shackle_id] = shackle
            audit.gate_candidates.append(shackle_id)

    def complete_audit(self, audit: SoulAudit) -> dict:
        """完成审计，生成最终报告"""
        audit.status = "completed"
        audit.completed_at = datetime.now().isoformat()

        # 计算总览
        total_shackles = len(audit.shackle_map)
        dimensions_with_shackles = set(s.dimension for s in audit.shackle_map.values())
        top_gate = audit.top_gates[0] if audit.top_gates else None

        report = {
            "audit_id": audit.id,
            "status": "completed",
            "summary": {
                "total_conversations": len(audit.conversation),
                "evasion_count": sum(1 for r in audit.conversation if r.evasion_detected),
                "shackles_identified": total_shackles,
                "dimensions_explored": len(dimensions_with_shackles),
                "first_gate": {
                    "name": top_gate.name,
                    "dimension": top_gate.dimension,
                    "priority": top_gate.gate_priority,
                    "description": top_gate.description,
                } if top_gate else None,
            },
            "shackle_map": {
                sid: {
                    "name": s.name,
                    "dimension": s.dimension,
                    "gate_priority": s.gate_priority,
                    "depth_score": s.depth_score,
                    "evasion_level": s.evasion_level,
                }
                for sid, s in audit.shackle_map.items()
            },
            "message": self._generate_completion_message(audit),
        }

        return report

    def _generate_completion_message(self, audit: SoulAudit) -> str:
        """生成审计完成消息"""
        if not audit.shackle_map:
            return (
                "你通过了灵魂审计，但没有识别出明显的枷锁。\n\n"
                "这有两种可能：\n"
                "1. 你已经非常自洽，没有需要突破的地方（罕见）\n"
                "2. 你的防御机制太强，我还没能穿透（更常见）\n\n"
                "建议一周后重新审计。带着更深的诚实来。"
            )

        top = audit.top_gates[0]
        return (
            f"灵魂审计完成。\n\n"
            f"我看到了你的窄门：**{top.name}**\n"
            f"维度：{top.dimension}\n"
            f"窄门优先级：{top.gate_priority:.0f}/100\n\n"
            f"这意味着——{top.description}\n\n"
            f"这是你最不想面对的，但也是你最需要穿越的。\n\n"
            f"穿越它，你就从凡人层进入了看见层。\n"
            f"不穿越，你会一直在原地打转。\n\n"
            f"选择权在你。"
        )


# ============================================================
# 导出
# ============================================================

__all__ = [
    "SoulAuditEngine",
    "SoulAudit",
    "Shackle",
    "AuditQuestion",
    "AuditResponse",
    "AUDIT_DIMENSIONS",
]
