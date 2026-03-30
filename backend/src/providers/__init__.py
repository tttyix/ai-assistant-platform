"""
AI 模型提供商
"""
from .base import BaseProvider, ChatMessage, ChatRequest, ChatResponse, ModelInfo
from .dashscope_provider import DashScopeProvider
from .model_registry import ModelRegistry, model_registry, init_providers

__all__ = [
    "BaseProvider",
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "ModelInfo",
    "DashScopeProvider",
    "ModelRegistry",
    "model_registry",
    "init_providers",
]
