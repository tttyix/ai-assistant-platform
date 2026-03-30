"""
Pydantic 数据模型
用于 API 请求和响应的验证
"""
from .chat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ConversationCreate,
    ConversationResponse,
    MessageResponse,
)
from .knowledge import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    DocumentResponse,
    KnowledgeQuery,
    QueryResult,
)

__all__ = [
    # Chat
    "ChatCompletionRequest",
    "ChatCompletionResponse",
    "ConversationCreate",
    "ConversationResponse",
    "MessageResponse",
    # Knowledge
    "KnowledgeBaseCreate",
    "KnowledgeBaseUpdate",
    "KnowledgeBaseResponse",
    "DocumentResponse",
    "KnowledgeQuery",
    "QueryResult",
]
