"""
窄门 (NarrowGate) — MIMO AI挑战生成器

用MIMO API动态生成穿越挑战，根据用户回答智能调整。

架构师：贾维斯 (Jarvis) for 小林医生
"""

import asyncio
from typing import List, Dict, Optional
from .mimo_client import MIMOClient
from .gate_finder import NarrowGate


class MIMOChallengeGenerator:
    """
    MIMO AI挑战生成器

    根据用户的窄门和进化状态，动态生成个性化挑战。
    """

    def __init__(self):
        self.mimo = MIMOClient()

    async def generate_challenge(
        self,
        gate: NarrowGate,
        day: int,
        user_history: List[Dict] = None,
        user_profile: str = "",
    ) -> Dict:
        """
        生成今天的挑战

        Args:
            gate: 窄门
            day: 第几天
            user_history: 用户过往挑战记录
            user_profile: 用户画像描述
        """
        # 难度递进
        if day <= 10:
            difficulty = "入门"
            difficulty_num = min(day, 5)
        elif day <= 20:
            difficulty = "中等"
            difficulty_num = min(day - 5, 7)
        else:
            difficulty = "高级"
            difficulty_num = min(day - 10, 10)

        system_prompt = f"""你是窄门平台的穿越训练引擎。

## 窄门信息
名称：{gate.name}
维度：{gate.dimension}
核心枷锁：{gate.description}
宽门路径：{gate.wide_gate_path}
窄门路径：{gate.narrow_gate_path}

## 当前状态
第{day}天 / 难度：{difficulty} ({difficulty_num}/10)

## 规则
1. 生成一个具体的、可执行的每日挑战
2. 挑战必须"难但正确"——用户最不想做但应该做
3. 挑战必须与窄门维度相关
4. 用中文，不超过60字
5. 不要解释，直接给挑战
6. 每个挑战必须有一个emoji
"""

        if user_profile:
            system_prompt += f"\n## 用户画像\n{user_profile}\n"

        if user_history:
            recent = user_history[-3:] if len(user_history) > 3 else user_history
            history_text = "\n".join([f"第{h.get('day','?')}天: {h.get('challenge','')} → {h.get('status','')}" for h in recent])
            system_prompt += f"\n## 近期挑战记录\n{history_text}\n"

        try:
            challenge = await self.mimo.chat(
                [{"role": "user", "content": f"生成第{day}天的穿越挑战"}],
                system_prompt,
                temperature=0.9,
            )
        except (ConnectionError, TimeoutError, Exception) as e:
            # Fallback to template
            import logging
            logging.getLogger("narrowgate").debug(f"MIMO挑战生成失败: {e}")
            challenge = self._get_fallback_challenge(gate, day)

        return {
            "challenge": challenge,
            "difficulty": difficulty_num,
            "day": day,
            "gate_name": gate.name,
            "dimension": gate.dimension,
        }

    async def generate_reflection_prompt(
        self,
        challenge: str,
        user_response: str,
    ) -> str:
        """
        根据用户完成挑战后的反馈，生成反思引导
        """
        system_prompt = """你是窄门平台的反思引擎。

用户刚完成一个穿越挑战。根据他们的反馈，生成一个简短的反思引导。

规则：
1. 不超过40字
2. 指向深层觉察
3. 用中文
4. 不要安慰，要启发
"""

        try:
            return await self.mimo.chat(
                [{"role": "user", "content": f"挑战：{challenge}\n用户反馈：{user_response}"}],
                system_prompt,
                temperature=0.8,
            )
        except Exception:
            return "在做的过程中，你发现了什么关于自己的真相？"

    def _get_fallback_challenge(self, gate: NarrowGate, day: int) -> str:
        """模板fallback"""
        templates = {
            "认知": [
                "📖 读一篇你完全不同意的文章，写下它3个可能对的地方",
                "🎯 跟一个你通常不会交谈的人进行10分钟深度对话",
                "💡 写下你最害怕别人发现的3个'不够好'的地方",
            ],
            "情绪": [
                "💧 在安全的环境里允许自己哭一次，感受情绪的流动",
                "🔥 对一个信任的人说出你最真实的感受",
                "🪞 写一封信给那个你一直在逃避的情绪",
            ],
            "行为": [
                "⚡ 现在就做你拖延最久的那件事的前15分钟",
                "🎯 公开承诺今天要完成一件事，然后完成它",
                "🔥 删掉手机上3个分散你注意力的App",
            ],
            "关系": [
                "🚪 今天对一个你不真正想做的事说'不'",
                "💬 告诉一个人你对某事的真实看法",
                "🪞 在一段关系中主动表达脆弱而不是保持坚强",
            ],
            "事业": [
                "🚀 大声说出你真正的事业目标",
                "📝 今天为那个'不可能的梦'做一件小事",
                "🎯 申请/报名一个你觉得'我不够格'的机会",
            ],
        }
        dim_challenges = templates.get(gate.dimension, templates["行为"])
        return dim_challenges[day % len(dim_challenges)]

    async def close(self):
        """关闭连接"""
        await self.mimo.close()


# 同步包装器
def generate_challenge_sync(gate, day, user_history=None):
    """同步生成挑战"""
    gen = MIMOChallengeGenerator()
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(gen.generate_challenge(gate, day, user_history))
    finally:
        loop.run_until_complete(gen.close())
        loop.close()


__all__ = ["MIMOChallengeGenerator", "generate_challenge_sync"]
