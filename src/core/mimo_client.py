"""
窄门 (NarrowGate) — MIMO API 适配器

接入小米MIMO API，为大师引导者提供真正的AI对话能力。

架构师：贾维斯 (Jarvis) for 小林医生
"""

import httpx
import asyncio
import json
from typing import List, Dict, Optional
from dataclasses import dataclass


MIMO_BASE_URL = "https://api.xiaomimimo.com/v1"
MIMO_API_KEY = "sk-ccwzuzw9e1t42xjok84nfx7wrv4geuzc590ojipwfqga5uxl"


@dataclass
class MIMOConfig:
    """MIMO API配置"""
    base_url: str = MIMO_BASE_URL
    api_key: str = MIMO_API_KEY
    model: str = "mimo-v2-flash"
    temperature: float = 0.7
    max_tokens: int = 1024
    timeout: int = 30


class MIMOClient:
    """
    MIMO API 客户端

    封装小米MIMO API调用，支持：
    - 单轮对话
    - 多轮对话（带历史）
    - 大师角色扮演
    """

    def __init__(self, config: MIMOConfig = None):
        self.config = config or MIMOConfig()
        self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=self.config.timeout,
            )
        return self._client

    async def chat(
        self,
        messages: List[Dict],
        system_prompt: str = "",
        temperature: float = None,
    ) -> str:
        """
        发送对话请求

        Args:
            messages: 对话历史 [{"role": "user/assistant", "content": "..."}]
            system_prompt: 系统提示词
            temperature: 温度参数

        Returns:
            AI回复文本
        """
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": self.config.model,
                    "messages": full_messages,
                    "temperature": temperature or self.config.temperature,
                    "max_tokens": self.config.max_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[MIMO API调用失败: {str(e)}]"

    async def master_converse(
        self,
        master_name: str,
        master_persona: str,
        master_style: str,
        user_message: str,
        conversation_history: List[Dict] = None,
        evasion_detected: bool = False,
        evasion_type: str = "",
    ) -> str:
        """
        大师对话

        根据大师的性格和风格，生成AI回复。
        """
        # 构建系统提示词
        system_prompt = f"""你是{master_name}，窄门平台的大师引导者。

## 你的身份
{master_persona}

## 你的追问风格
{master_style}

## 对话规则
1. 永远用第一人称，不要说"作为AI"
2. 回复要简短有力，不超过150字
3. 每次回复最多一个问题
4. 不要用"我理解你的感受"这种空话
5. 直接、锋利、不客套
6. 用中文回复
"""

        if evasion_detected:
            system_prompt += f"""
## ⚠️ 回避检测
用户正在{evasion_type}。不要接受表面回答。
用你的方式指出回避，然后追问。
"""

        # 构建消息历史
        messages = conversation_history or []
        messages.append({"role": "user", "content": user_message})

        return await self.chat(messages, system_prompt, temperature=0.8)

    async def soul_audit_question(
        self,
        dimension: str,
        depth: int,
        user_answer: str,
        evasion_detected: bool,
        evasion_type: str,
    ) -> str:
        """
        生成灵魂审计追问
        """
        system_prompt = f"""你是窄门平台的灵魂审计引擎。你的任务是深度追问，不接受表面答案。

## 当前维度：{dimension}
## 当前深度层级：{depth}/4（1=表面，4=核心直击）

## 规则
1. 回复是一个追问，不超过80字
2. 不要解释，不要安慰，直接问
3. 深度{depth}时的策略：
   - 1: 开放式探索
   - 2: 指向矛盾和回避
   - 3: 强迫量化自我评价
   - 4: 击穿所有防御，问最核心的问题
4. 用中文
"""

        if evasion_detected:
            system_prompt += f"""
## ⚠️ 回避检测
用户回答中检测到{evasion_type}回避。追问要指向回避本身。
"""

        user_msg = f"用户回答：{user_answer}"
        return await self.chat(
            [{"role": "user", "content": user_msg}],
            system_prompt,
            temperature=0.9,
        )

    async def close(self):
        """关闭连接"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# ============================================================
# 同步包装器
# ============================================================

def sync_chat(messages, system_prompt="", config=None):
    """同步调用MIMO API"""
    client = MIMOClient(config)
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(client.chat(messages, system_prompt))
    finally:
        loop.run_until_complete(client.close())
        loop.close()


# ============================================================
# 导出
# ============================================================

__all__ = ["MIMOClient", "MIMOConfig", "sync_chat"]
