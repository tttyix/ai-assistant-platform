"""
模型注册表
统一管理所有 AI 模型提供商
"""
from typing import Dict, List, Optional
from .base import BaseProvider, ChatRequest, ChatResponse, ModelInfo
from .dashscope_provider import DashScopeProvider


class ModelRegistry:
    """
    模型注册表

    统一管理所有 AI 模型提供商，提供：
    - 提供商注册和管理
    - 模型到提供商的映射
    - 智能路由对话请求
    """

    def __init__(self):
        """初始化模型注册表"""
        self.providers: Dict[str, BaseProvider] = {}
        self.model_to_provider: Dict[str, str] = {}

    def register_provider(self, name: str, provider: BaseProvider):
        """
        注册 AI 模型提供商

        Args:
            name: 提供商名称（如 "dashscope", "openai"）
            provider: 提供商实例
        """
        self.providers[name] = provider

        # 注册模型映射
        for model in provider.get_models():
            self.model_to_provider[model.id] = name
            print(f"  - {model.id} ({model.name})")

    def get_provider(self, model_id: str) -> Optional[BaseProvider]:
        """
        根据模型 ID 获取对应的提供商

        Args:
            model_id: 模型 ID（如 "qwen-max"）

        Returns:
            BaseProvider: 提供商实例，如果模型不存在则返回 None
        """
        provider_name = self.model_to_provider.get(model_id)
        if provider_name:
            return self.providers.get(provider_name)
        return None

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        智能路由对话请求到对应的提供商

        Args:
            request: 对话请求

        Returns:
            ChatResponse: 对话响应

        Raises:
            ValueError: 当模型不存在时抛出
        """
        provider = self.get_provider(request.model)
        if not provider:
            raise ValueError(f"未知模型：{request.model}")
        return await provider.chat(request)

    async def stream_chat(self, request: ChatRequest):
        """
        智能路由流式对话请求到对应的提供商

        Args:
            request: 对话请求

        Yields:
            str: 对话内容片段

        Raises:
            ValueError: 当模型不存在时抛出
        """
        provider = self.get_provider(request.model)
        if not provider:
            raise ValueError(f"未知模型：{request.model}")
        async for chunk in provider.stream_chat(request):
            yield chunk

    def get_all_models(self) -> List[ModelInfo]:
        """
        获取所有可用模型

        Returns:
            List[ModelInfo]: 模型信息列表
        """
        models = []
        for provider in self.providers.values():
            models.extend(provider.get_models())
        return models


# 全局注册表实例
model_registry = ModelRegistry()


def init_providers(settings) -> ModelRegistry:
    """
    初始化所有 AI 模型提供商

    Args:
        settings: 应用配置

    Returns:
        ModelRegistry: 初始化后的模型注册表
    """
    print("正在初始化 AI 模型提供商...")

    # 注册通义千问
    if settings.DASHSCOPE_API_KEY:
        dashscope = DashScopeProvider(settings.DASHSCOPE_API_KEY)
        model_registry.register_provider("dashscope", dashscope)
        print("✅ 通义千问提供商已注册")

    # OpenAI（可选）
    # if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
    #     from .openai_provider import OpenAIProvider
    #     openai = OpenAIProvider(settings.OPENAI_API_KEY)
    #     model_registry.register_provider("openai", openai)
    #     print("✅ OpenAI 提供商已注册")

    # Anthropic（可选）
    # if hasattr(settings, 'ANTHROPIC_API_KEY') and settings.ANTHROPIC_API_KEY:
    #     from .anthropic_provider import AnthropicProvider
    #     anthropic = AnthropicProvider(settings.ANTHROPIC_API_KEY)
    #     model_registry.register_provider("anthropic", anthropic)
    #     print("✅ Anthropic 提供商已注册")

    print(f"✅ 已注册 {len(model_registry.providers)} 个提供商")
    print(f"✅ 可用模型：{len(model_registry.get_all_models())} 个")

    return model_registry
