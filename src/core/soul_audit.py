"""
窄门 (NarrowGate) — 灵魂审计引擎 (Soul Audit Engine)

核心哲学：不接受表面答案，持续追问直到真相浮现。
这是鉴别诊断思维在个人成长领域的应用。

架构师：贾维斯 (Jarvis) for 小林医生
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field


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
    # ═══════════════════════════════════════════════════════════
    # 维度1：认知 — 思维模式、信念系统、世界观
    # ═══════════════════════════════════════════════════════════
    "认知": {
        "description": "你的思维模式、信念系统、世界观",
        "surface_questions": [
            "你觉得自己的人生到现在，最大的成就是什么？",
            "你认为成功最重要的因素是什么？",
            "你最近一次改变一个长期持有的观点是什么时候？",
            "你最崇拜的人是谁？你崇拜TA的什么？",
            "你觉得什么是'聪明'？你认为自己聪明吗？",
            "你做决策时，更多依赖直觉还是逻辑？",
        ],
        "mid_questions": [
            "你有没有发现——你崇拜的那个人的特质，其实恰恰是你觉得自己缺少的？",
            "你定义'成功'的标准，是你自己定的，还是从别人那里借来的？",
            "你害怕自己不够聪明这件事，是从什么时候开始的？",
            "你有没有在某件事上一直'假装懂'，但其实从没真正理解过？",
            "如果所有人都消失了，你还会追求你现在追求的东西吗？",
        ],
        "deep_questions": [
            "你认为这个世界是物质的，还是意识的？为什么？",
            "如果一切都是频率和振动，你觉得自己的'频率'在什么状态？",
            "你感知到的现实，是世界的真相，还是你认知滤镜的投射？",
            "你有没有怀疑过——你一直相信的'真实'，可能只是一个故事？",
            "你对'自我'的理解——是来自你的思考，还是来自别人对你的定义？",
            "如果让你用三个词定义自己——这三个词是你选择的，还是被赋予的？",
        ],
        "core_questions": [
            "你有没有一个从未说出口的信念——你内心深处觉得它是对的，但不敢说因为会被嘲笑？",
            "如果今天是你人生的最后一天，你觉得你这辈子最荒谬的执念是什么？",
            "你有没有在深夜突然觉得——你一直在追逐的一切，可能根本没有意义？那一刻你看到了什么？",
            "假如你不是你——你会怎么看现在的自己？你会给出什么建议？",
        ],
        "evasion_patterns": ["宏大叙事回避细节", "用别人的标准定义成功", "把运气当能力"],
        "related_masters": ["socrates", "alchemist"],
        "related_course_days": [3, 4, 5, 12, 13],
    },

    # ═══════════════════════════════════════════════════════════
    # 维度2：情绪 — 感受、表达、压抑
    # ═══════════════════════════════════════════════════════════
    "情绪": {
        "description": "你如何感受、表达、压抑情绪",
        "surface_questions": [
            "你上一次真正生气是什么时候？因为什么？",
            "什么事情会让你感到羞耻？",
            "你最害怕别人发现你什么？",
            "你上次哭是什么时候？在谁面前？",
            "你有没有对某个人又爱又恨？",
            "什么事情会瞬间让你感到焦虑？",
        ],
        "mid_questions": [
            "你生气的时候，第一反应是发出来还是压下去？",
            "你有没有发现你的焦虑总是在特定时间或场景出现？",
            "你允许自己在别人面前软弱吗？如果不能，为什么？",
            "你觉得你的父母处理情绪的方式，是不是你的模板？",
            "你有没有用'忙'来逃避感受某种情绪？",
        ],
        "deep_questions": [
            "你的愤怒、恐惧、悲伤——是'你'，还是经过你的能量？",
            "你有没有发现，你压抑的情绪总会在别处爆发？",
            "如果情绪是频率，你的日常情绪在什么'赫兹'？",
            "你最深层的恐惧是什么——不是表面的怕蜘蛛、怕演讲——而是那个让你夜里睡不着的？",
            "你有没有一种情绪，是从小到大一直存在的？它在告诉你什么？",
        ],
        "core_questions": [
            "你有没有一种感觉——觉得自己不值得被爱？这种感觉从哪里来的？",
            "如果让你直视你内心最深的伤疤——它是什么？你花了多少精力在保护它？",
            "你有没有在某个瞬间感受到纯粹的、无条件的爱？那个瞬间是什么样的？",
            "如果情绪是信使——你最近收到的最重要的信是什么？你读懂了吗？",
        ],
        "evasion_patterns": ["我不太有情绪", "都过去了", "别人都这样"],
        "related_masters": ["jung", "mirror"],
        "related_course_days": [6, 7, 8, 14, 15],
    },

    # ═══════════════════════════════════════════════════════════
    # 维度3：行为 — 习惯、执行力、自律
    # ═══════════════════════════════════════════════════════════
    "行为": {
        "description": "你的习惯、执行力、自律模式",
        "surface_questions": [
            "你明知道应该做但一直没做的事情是什么？",
            "你每天花时间最多的事情是什么？",
            "你上次为一个目标坚持超过三个月是什么时候？",
            "你今天的作息是什么样的？满意吗？",
            "你有没有一个坚持了很久的习惯？它给你带来了什么？",
            "你手机屏幕使用时间是多少？你对这个数字怎么看？",
        ],
        "mid_questions": [
            "你的拖延，背后真的只是懒，还是对某种结果的深层恐惧？",
            "你一直在重复的行为模式，从哪里学来的？是你的选择还是被编程？",
            "你有没有一个'每次发誓再也不做但还是会做'的行为？",
            "你觉得自己执行力不行，是真的不行，还是只对特定事情不行？",
            "你有没有在用'完美主义'来为自己的不行动找借口？",
        ],
        "deep_questions": [
            "如果你的行为是一本书——别人读了会得出什么结论？这个结论和你对自己的认知一致吗？",
            "你最想改变自己的一件事，你试过几次了？为什么每次都失败？",
            "你有没有发现你在某些场景下会变成'另一个人'？那个'另一个人'是谁？",
            "你觉得你的习惯是在帮你还是在困住你？哪些习惯是你自己选择的，哪些是被环境塑造的？",
        ],
        "core_questions": [
            "你有没有一直在重复一个行为模式，每次结果都不好，但你还是在做——你在通过这个行为逃避什么？",
            "如果你今天的全部行为被拍成纪录片——你敢让你最尊重的人看吗？",
            "你有没有一种'被困住'的感觉？那个困住你的东西，真的是外部环境，还是你自己？",
        ],
        "evasion_patterns": ["太忙了", "还没准备好", "条件不允许"],
        "related_masters": ["memento", "socrates"],
        "related_course_days": [1, 2, 9, 10, 11],
    },

    # ═══════════════════════════════════════════════════════════
    # 维度4：关系 — 连接、边界、依赖
    # ═══════════════════════════════════════════════════════════
    "关系": {
        "description": "你与他人的连接模式、边界、依赖",
        "surface_questions": [
            "你最亲近的人，你觉得他们真正了解你吗？",
            "你有没有维持着一段让你不舒服但不敢结束的关系？",
            "你帮过别人最大的忙是什么？你为什么帮？",
            "你最好的朋友是谁？你们多久联系一次？",
            "你上次跟人吵架是因为什么？",
            "你觉得你是讨好型人格吗？",
        ],
        "mid_questions": [
            "你最亲近的人——你对他们的感情里，有多少是爱，多少是依赖？",
            "你在关系中扮演的角色——是照顾者、被照顾者、还是两者都有？",
            "你有没有一段关系里，你一直在付出但很少被回报？为什么你还在？",
            "你觉得你被真正理解过吗？被谁？",
            "你害怕被抛弃吗？这种恐惧从哪里来？",
        ],
        "deep_questions": [
            "你吸引来的人，是你的频率的镜子——你从他们身上看到了什么？",
            "人性的本质是善还是恶？还是善恶本身就是幻觉？",
            "你觉得人与人之间是分离的，还是一体的？",
            "你有没有发现你在重复父母的婚姻/关系模式？",
            "你在关系中最害怕的是什么——被看见，还是不被看见？",
        ],
        "core_questions": [
            "如果你能对一个人说一句话，而TA必须完全理解你的意思——你会对谁说什么？",
            "你在关系中最深的创伤是什么？它如何塑造了你现在的关系模式？",
            "你觉得你值得被无条件地爱吗？如果你说'是'——你真的相信吗？",
        ],
        "evasion_patterns": ["我人缘挺好的", "都是别人的问题", "我不需要别人"],
        "related_masters": ["mirror", "jung"],
        "related_course_days": [16, 17, 18, 19, 20],
    },

    # ═══════════════════════════════════════════════════════════
    # 维度5：事业 — 野心、恐惧、能力与现实的差距
    # ═══════════════════════════════════════════════════════════
    "事业": {
        "description": "你的野心、恐惧、能力与现实的差距",
        "surface_questions": [
            "如果没有任何限制，你真正想做什么？",
            "你觉得现在配得上自己想要的位置吗？",
            "你有没有在用'还没准备好'来逃避一个你其实可以开始的事情？",
            "你上一次全力以赴做一件事是什么时候？",
            "你工作中最有成就感的时刻是什么？",
            "你觉得你做到了你能力的百分之多少？",
        ],
        "mid_questions": [
            "你追求的到底是你真正想要的，还是社会告诉你'应该'想要的？",
            "如果明天一切清零，你还会做现在做的事吗？",
            "你有没有发现自己在跟别人比较，然后感到焦虑？你比较的标准是什么？",
            "你害怕失败，还是害怕成功？",
            "你的事业目标，是你给自己定的，还是你父母/社会给你定的？",
        ],
        "deep_questions": [
            "你有没有想过——你一直在努力证明的那个东西，可能根本不需要证明？",
            "你最大的才能是什么？你用了多少？为什么没有更多地用它？",
            "如果你已经成功了——你还会在意别人怎么看你吗？",
            "你有没有在潜意识里害怕自己太成功？",
        ],
        "core_questions": [
            "你内心深处真正想要的，不是你对别人说的那个——到底是什么？",
            "如果你永远无法'成功'——你的人生还有意义吗？那个意义是什么？",
            "你有没有一种感觉——觉得你的人生被'应该'劫持了，而不是在活'想要'？",
        ],
        "evasion_patterns": ["这是人之常情", "大家都这样想", "这是现实不是幻觉"],
        "related_masters": ["architect", "memento"],
        "related_course_days": [21, 22, 23, 24, 25],
    },

    # ═══════════════════════════════════════════════════════════
    # 维度6：宇宙认知 — 对世界、人性、神性的底层认知
    # ═══════════════════════════════════════════════════════════
    "宇宙认知": {
        "description": "你对世界、人性、神性的底层认知",
        "surface_questions": [
            "你觉得人生有目的吗？如果有，是什么？",
            "你相信命运吗？还是一切都是随机的？",
            "你觉得人死后会怎样？",
            "你有宗教信仰吗？如果有，为什么？",
            "你觉得宇宙是善意的还是冷漠的？",
            "你有没有过'似曾相识'的感觉？你怎么解释它？",
        ],
        "mid_questions": [
            "你觉得你的存在是偶然还是必然？",
            "如果宇宙有意识——你觉得它在通过你体验什么？",
            "你有没有在大自然中感受到过某种'更大'的存在？",
            "你相信直觉吗？你的直觉准确率有多高？",
            "你觉得巧合是真的巧合，还是某种安排？",
        ],
        "deep_questions": [
            "如果宇宙的本质是振动和能量，你觉得'你'是什么？",
            "你有没有在某个瞬间感受到过'万物一体'？那是什么感觉？",
            "神性——你认为是外在的神，还是你内在的一部分？",
            "《与神对话》说：'神对每个人说话，时刻不停。问题是谁在听。'——你在听吗？",
            "你对人性的认知，是来自你的体验，还是来自被灌输的观念？",
            "如果恐惧是低频，爱是高频——你大部分时间在哪个频率？",
        ],
        "core_questions": [
            "如果一切都是命中注定——你现在的选择还有意义吗？如果有，意义在哪里？",
            "你有没有一种深层的直觉——关于你这辈子到底要来做什么？",
            "如果你知道死后会发生什么——你会改变今天的活法吗？",
        ],
        "evasion_patterns": ["我不信这些", "这是哲学问题", "想这些没用"],
        "related_masters": ["alchemist", "gatekeeper"],
        "related_course_days": [26, 27, 28, 29, 30],
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

        四层递进：
        1. 表层 (depth=1)：开放式探索，建立信任
        2. 中层 (depth=2)：开始挖掘，引入矛盾
        3. 深层 (depth=3)：直击痛点，暴露回避
        4. 核心 (depth=4)：剥离伪装，触及真相
        """
        dimension = audit.current_dimension
        dim_info = AUDIT_DIMENSIONS[dimension]
        depth = audit.current_depth
        last_response = audit.conversation[-1] if audit.conversation else None

        # 如果检测到回避，先追回避
        if last_response and last_response.evasion_detected:
            return self._build_evasion_followup(audit, last_response, dimension, depth)

        if depth == 1:
            qs = dim_info["surface_questions"]
            idx = len([c for c in audit.conversation if c.dimension == dimension and c.depth_level == 1]) % len(qs)
            return AuditQuestion(
                question=qs[idx], dimension=dimension, depth_level=1,
                purpose="探索表层认知", expected_evasion="标准化答案",
            )

        elif depth == 2:
            qs = dim_info.get("mid_questions", dim_info.get("deep_questions", []))
            if qs:
                idx = len([c for c in audit.conversation if c.dimension == dimension and c.depth_level == 2]) % len(qs)
                question = qs[idx]
            else:
                question = f"在{dimension}这个维度上，你觉得自己的最大短板是什么？为什么到现在还没解决？"
            return AuditQuestion(
                question=question, dimension=dimension, depth_level=2,
                purpose="中层挖掘，引入矛盾", expected_evasion="更深的合理化",
            )

        elif depth == 3:
            qs = dim_info.get("deep_questions", [])
            if qs:
                idx = len([c for c in audit.conversation if c.dimension == dimension and c.depth_level == 3]) % len(qs)
                question = qs[idx]
            else:
                question = f"如果让你在{dimension}方面对自己做一个残酷的诚实评价，满分10分你给自己打几分？扣掉的分丢在哪里了？"
            return AuditQuestion(
                question=question, dimension=dimension, depth_level=3,
                purpose="深层直击，暴露回避", expected_evasion="模糊化/转移",
            )

        else:
            qs = dim_info.get("core_questions", [])
            if qs:
                idx = len([c for c in audit.conversation if c.dimension == dimension and c.depth_level == 4]) % len(qs)
                question = qs[idx]
            else:
                question = f"在{dimension}方面，你有没有一个从未告诉任何人的秘密？关于你是谁、你做过什么、或者你真正想要什么？"
            return AuditQuestion(
                question=question, dimension=dimension, depth_level=4,
                purpose="击穿所有防御机制", expected_evasion="强烈抵抗或突破",
            )

    def _build_evasion_followup(self, audit, last_response, dimension, depth) -> AuditQuestion:
        """针对回避模式生成追问"""
        followups = {
            "否认": [
                f"你说\"{last_response.answer[:20]}\"——但我感觉这不是全部。在这层回答下面，是什么？",
                f"如果我告诉你'没有感觉'也是一种感觉——你会怎么重新回答刚才的问题？",
                "没关系，大多数人的第一反应都是否认。但我们继续——你真的觉得没什么特别的吗？",
            ],
            "转移": [
                f"你刚才转移了话题。这意味着刚才的问题触碰到了某个敏感区域。让我们回到那个点——",
                "我注意到你在转移。这说明里面有东西。我们不需要急，慢慢来。",
            ],
            "最小化": [
                f"'一点点'、'还好'——这些词是在给自己的回避找台阶。真实感受是什么？",
                "如果这不是'还好'，而是'非常重要'——你会怎么重新描述它？",
            ],
            "合理化": [
                f"每个'因为'后面都藏着一个真正的恐惧。抛开理由，你的直觉告诉你什么？",
                "你的理由很合理。但合理和真实是两回事。抛开理由——你真正害怕的是什么？",
            ],
            "攻击": [
                "你在攻击问题本身。这意味着问题击中了要害。我不会退让——回答它。",
                "你对这个问题的反应比答案本身更说明问题。你在保护什么？",
            ],
            "回避—过短回答": [
                "你的回答太短了。这不是你不想说——是你还没准备好面对它。再试一次，多说一些。",
                "给我三个句子。不需要深刻，但需要真实。",
            ],
        }
        evasion_type = last_response.evasion_type.split("—")[0] if "—" in last_response.evasion_type else last_response.evasion_type
        options = followups.get(evasion_type, followups["否认"])
        idx = len([c for c in audit.conversation if c.evasion_detected]) % len(options)
        return AuditQuestion(
            question=options[idx], dimension=dimension, depth_level=depth,
            purpose=f"追回避：{evasion_type}", expected_evasion="更深层的回避或突破",
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

    def generate_course_recommendation(self, audit: SoulAudit) -> dict:
        """根据审计结果生成个性化课程推荐"""
        if not audit.shackle_map:
            return {
                "crossing_path": [f"D{d}" for d in range(1, 15)],
                "primary_dimension": "认知",
                "recommended_masters": ["socrates"],
                "starting_day": 1,
                "reasoning": "未识别出明确枷锁，建议从第1天开始全面探索。",
            }

        dim_shackles = {}
        for s in audit.shackle_map.values():
            dim_shackles.setdefault(s.dimension, []).append(s)

        sorted_dims = sorted(dim_shackles.items(),
                             key=lambda x: max(s.gate_priority for s in x[1]),
                             reverse=True)
        primary_dim = sorted_dims[0][0]

        recommended_days = set()
        for dim, _ in sorted_dims[:3]:
            for day in AUDIT_DIMENSIONS.get(dim, {}).get("related_course_days", []):
                recommended_days.add(day)

        recommended_masters = []
        for dim, _ in sorted_dims[:2]:
            for mid in AUDIT_DIMENSIONS.get(dim, {}).get("related_masters", []):
                if mid not in recommended_masters:
                    recommended_masters.append(mid)

        crossing_path = sorted(recommended_days)[:14]
        if len(crossing_path) < 7:
            crossing_path = list(range(1, 15))

        top_gate = audit.top_gates[0]
        return {
            "crossing_path": [f"D{d}" for d in crossing_path],
            "primary_dimension": primary_dim,
            "primary_gate": {"name": top_gate.name, "dimension": top_gate.dimension, "priority": top_gate.gate_priority},
            "recommended_masters": recommended_masters[:3],
            "starting_day": crossing_path[0],
            "reasoning": f"你的核心窄门是【{top_gate.name}】（{top_gate.dimension}维度），窄门优先级{top_gate.gate_priority:.0f}/100。我为你定制了一条{len(crossing_path)}天的穿越路线。",
            "dimension_analysis": {dim: {"shackle_count": len(shackles), "max_priority": max(s.gate_priority for s in shackles)} for dim, shackles in sorted_dims},
        }

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
