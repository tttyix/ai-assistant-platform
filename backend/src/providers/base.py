"""
AI 模型提供商基础接口
定义所有 AI 模型提供商的统一接口
"""
from abc import ABC, abstractmethod
from typing import List, Dict, AsyncIterator
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """对话消息模型"""
    role: str  # user, assistant, system
    content: str


class ChatRequest(BaseModel):
    """对话请求模型"""
    messages: List[ChatMessage]
    model: str
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = False


class ChatResponse(BaseModel):
    """对话响应模型"""
    content: str
    model: str
    tokens_used: Dict[str, int]
    finish_reason: str


class ModelInfo(BaseModel):
    """模型信息模型"""
    id: str
    name: str
    provider: str
    max_tokens: int
    cost_per_1k_tokens: Dict[str, float]


class BaseProvider(ABC):
    """
    AI 模型提供商基础接口

    所有 AI 模型提供商（OpenAI、Anthropic、通义千问等）
    都需要继承此抽象类并实现相应方法
    """

    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        非流式对话

        Args:
            request: 对话请求

        Returns:
            ChatResponse: 对话响应
        """
        pass

    @abstractmethod
    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[str]:
        """
        流式对话

        Args:
            request: 对话请求

        Yields:
            str: 对话内容片段
        """
        pass

    @abstractmethod
    def get_models(self) -> List[ModelInfo]:
        """
        获取可用模型列表

        Returns:
            List[ModelInfo]: 模型信息列表
        """
        pass
