"""
窄门 (NarrowGate) — 见证人网络 (Witness Network)

核心哲学：你的进化需要被看见。
不是社交媒体的点赞，是真实的人类见证。

架构师：贾维斯 (Jarvis) for 小林医生
"""

import uuid
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field


# ============================================================
# 数据模型
# ============================================================

@dataclass
class Witness:
    """见证人"""
    id: str
    name: str
    email: str = ""
    relationship: str = ""  # 朋友/家人/同事/导师/随机
    verified: bool = False  # 是否已验证
    created_at: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "relationship": self.relationship,
            "verified": self.verified,
        }


@dataclass
class WitnessVerification:
    """见证验证"""
    id: str
    witness_id: str
    crossing_id: str
    day: int
    challenge: str
    verified: bool = False
    message: str = ""  # 见证人留言
    timestamp: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "witness_id": self.witness_id,
            "day": self.day,
            "challenge": self.challenge,
            "verified": self.verified,
            "message": self.message,
        }


@dataclass
class WitnessGroup:
    """见证人小组"""
    id: str
    name: str
    members: List[str] = field(default_factory=list)  # witness IDs
    crossing_ids: List[str] = field(default_factory=list)  # 关联的穿越
    max_members: int = 5
    created_at: str = ""

    def add_member(self, witness_id: str) -> bool:
        if len(self.members) < self.max_members:
            self.members.append(witness_id)
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "member_count": len(self.members),
            "max_members": self.max_members,
        }


# ============================================================
# 见证人网络引擎
# ============================================================

class WitnessNetwork:
    """
    见证人网络

    核心机制：
    1. 选择1-5个见证人（必须是真实的人）
    2. 见证人每天收到你的挑战和完成情况
    3. 见证人可以验证/评论
    4. 见证人群组互助

    设计哲学：
    - 不是社交网络，是进化加速器
    - 每个见证人必须是真实的人
    - 最多5个——质量>数量
    """

    def __init__(self):
        self._witnesses: Dict[str, Witness] = {}
        self._verifications: Dict[str, List[WitnessVerification]] = {}
        self._groups: Dict[str, WitnessGroup] = {}

    # ============================================================
    # 见证人管理
    # ============================================================

    def add_witness(
        self,
        name: str,
        email: str = "",
        relationship: str = "朋友",
    ) -> Witness:
        """添加见证人"""
        witness_id = f"witness_{uuid.uuid4().hex[:8]}"
        now = datetime.now().isoformat()

        witness = Witness(
            id=witness_id,
            name=name,
            email=email,
            relationship=relationship,
            created_at=now,
        )
        self._witnesses[witness_id] = witness
        return witness

    def get_witness(self, witness_id: str) -> Optional[Witness]:
        """获取见证人"""
        return self._witnesses.get(witness_id)

    def get_all_witnesses(self) -> List[Witness]:
        """获取所有见证人"""
        return list(self._witnesses.values())

    # ============================================================
    # 见证流程
    # ============================================================

    def send_verification_request(
        self,
        witness_id: str,
        crossing_id: str,
        day: int,
        challenge: str,
    ) -> WitnessVerification:
        """发送验证请求"""
        verification_id = f"verify_{uuid.uuid4().hex[:8]}"
        now = datetime.now().isoformat()

        verification = WitnessVerification(
            id=verification_id,
            witness_id=witness_id,
            crossing_id=crossing_id,
            day=day,
            challenge=challenge,
            timestamp=now,
        )

        if crossing_id not in self._verifications:
            self._verifications[crossing_id] = []
        self._verifications[crossing_id].append(verification)

        return verification

    def process_verification(
        self,
        verification_id: str,
        crossing_id: str,
        approved: bool,
        message: str = "",
    ) -> WitnessVerification:
        """处理验证结果"""
        verifications = self._verifications.get(crossing_id, [])
        for v in verifications:
            if v.id == verification_id:
                v.verified = approved
                v.message = message
                return v
        raise ValueError(f"验证记录不存在: {verification_id}")

    def get_verifications(self, crossing_id: str) -> List[WitnessVerification]:
        """获取穿越的所有验证记录"""
        return self._verifications.get(crossing_id, [])

    def get_witness_report(self, crossing_id: str) -> dict:
        """生成见证报告"""
        verifications = self.get_verifications(crossing_id)
        verified = sum(1 for v in verifications if v.verified)
        total = len(verifications)

        return {
            "crossing_id": crossing_id,
            "total_verifications": total,
            "verified": verified,
            "verification_rate": f"{verified / max(total, 1) * 100:.0f}%",
            "recent_verifications": [
                v.to_dict() for v in verifications[-5:]
            ],
        }

    # ============================================================
    # 见证人群组
    # ============================================================

    def create_group(self, name: str) -> WitnessGroup:
        """创建见证人群组"""
        group_id = f"group_{uuid.uuid4().hex[:8]}"
        group = WitnessGroup(
            id=group_id,
            name=name,
            created_at=datetime.now().isoformat(),
        )
        self._groups[group_id] = group
        return group

    def join_group(self, group_id: str, witness_id: str) -> bool:
        """加入群组"""
        group = self._groups.get(group_id)
        if not group:
            return False
        return group.add_member(witness_id)

    def get_group(self, group_id: str) -> Optional[WitnessGroup]:
        """获取群组"""
        return self._groups.get(group_id)


# ============================================================
# 导出
# ============================================================

__all__ = [
    "WitnessNetwork",
    "Witness",
    "WitnessVerification",
    "WitnessGroup",
]
