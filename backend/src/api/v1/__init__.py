"""
API v1 路由
"""
from .chat import router as chat_router
from .knowledge import router as knowledge_router
from .models import router as models_router
from .workflows import router as workflows_router

__all__ = [
    "chat_router",
    "knowledge_router",
    "models_router",
]
