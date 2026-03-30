"""
通义千问 AI 模型提供商
使用阿里云 DashScope API
"""
import httpx
import json
from typing import List, AsyncIterator
from .base import BaseProvider, ChatRequest, ChatResponse, ModelInfo


class DashScopeProvider(BaseProvider):
    """
    阿里云通义千问提供商

    支持模型：
    - qwen-max: 最强性能，适合复杂任务
    - qwen-plus: 平衡性能和成本
    - qwen-turbo: 最快速度，适合简单任务
    """

    def __init__(self, api_key: str):
        """
        初始化通义千问提供商

        Args:
            api_key: 阿里云 DashScope API 密钥
        """
        self.api_key = api_key
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=60.0
        )

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        非流式对话

        Args:
            request: 对话请求

        Returns:
            ChatResponse: 对话响应

        Raises:
            httpx.HTTPStatusError: API 请求失败时抛出
        """
        response = await self.client.post(
            "/chat/completions",
            json={
                "model": request.model,
                "messages": [
                    {"role": m.role, "content": m.content}
                    for m in request.messages
                ],
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "stream": False
            }
        )
        response.raise_for_status()
        data = response.json()

        return ChatResponse(
            content=data["choices"][0]["message"]["content"],
            model=data["model"],
            tokens_used=data.get("usage", {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }),
            finish_reason=data["choices"][0]["finish_reason"]
        )

    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[str]:
        """
        流式对话

        Args:
            request: 对话请求

        Yields:
            str: 对话内容片段
        """
        async with self.client.stream(
            "POST",
            "/chat/completions",
            json={
                "model": request.model,
                "messages": [
                    {"role": m.role, "content": m.content}
                    for m in request.messages
                ],
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "stream": True
            }
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # 移除 "data: " 前缀
                    if data != "[DONE]":
                        try:
                            chunk = json.loads(data)
                            delta = chunk["choices"][0]["delta"]
                            if delta.get("content"):
                                yield delta["content"]
                        except (json.JSONDecodeError, KeyError):
                            # 跳过无效的 chunk
                            continue

    def get_models(self) -> List[ModelInfo]:
        """
        获取通义千问可用模型列表

        Returns:
            List[ModelInfo]: 模型信息列表
        """
        return [
            ModelInfo(
                id="qwen-max",
                name="通义千问 Max",
                provider="dashscope",
                max_tokens=6000,
                cost_per_1k_tokens={"input": 0.04, "output": 0.12}
            ),
            ModelInfo(
                id="qwen-plus",
                name="通义千问 Plus",
                provider="dashscope",
                max_tokens=32000,
                cost_per_1k_tokens={"input": 0.004, "output": 0.012}
            ),
            ModelInfo(
                id="qwen-turbo",
                name="通义千问 Turbo",
                provider="dashscope",
                max_tokens=6000,
                cost_per_1k_tokens={"input": 0.002, "output": 0.006}
            ),
        ]
