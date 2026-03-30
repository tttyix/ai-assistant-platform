"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import get_settings
from .api.v1 import chat_router, knowledge_router, models_router, workflows_router
from .providers.model_registry import init_providers
from .database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    启动时初始化：
    - 数据库表
    - AI 模型提供商
    - RAG 服务

    关闭时清理资源
    """
    # 启动时初始化
    print(f"\n{'='*50}")
    print(f"START: {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"{'='*50}\n")

    # 初始化数据库
    print("正在初始化数据库...")
    try:
        init_db()
        print("OK: 数据库初始化完成")
    except Exception as e:
        print(f"Warning: 数据库初始化失败：{e}")

    # 初始化 AI 模型提供商
    print("\n正在初始化 AI 模型提供商...")
    try:
        init_providers(settings)
    except Exception as e:
        print(f"Warning: AI 模型提供商初始化失败：{e}")

    # 输出配置信息
    print(f"\nINFO: 配置信息:")
    print(f"   PostgreSQL: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
    print(f"   Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    print(f"   Qdrant: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
    print(f"   MinIO: {settings.MINIO_ENDPOINT}")
    print(f"   知识库：{settings.KNOWLEDGE_BASE_PATH}")
    print(f"\n{'='*50}\n")

    yield

    # 关闭时清理
    print("\n👋 应用关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="企业级 AI 助手集成平台，集成知识库和 RAG 能力",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat_router, prefix=f"{settings.API_PREFIX}/chat", tags=["💬 智能对话"])
app.include_router(knowledge_router, prefix=f"{settings.API_PREFIX}/knowledge", tags=["📚 知识库管理"])
app.include_router(models_router, prefix=f"{settings.API_PREFIX}/models", tags=["🤖 AI 模型"])
app.include_router(workflows_router, prefix=f"{settings.API_PREFIX}/workflows", tags=["⚡ 工作流协作"])


@app.get("/")
async def root():
    """
    根路径
    返回应用基本信息
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """
    健康检查接口
    用于负载均衡和服务监控
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


@app.get("/api")
async def api_info():
    """
    API 信息
    返回所有可用的 API 端点
    """
    return {
        "chat": {
            "completions": "POST /api/v1/chat/completions",
            "conversations": "GET/POST /api/v1/chat/conversations",
            "messages": "GET /api/v1/chat/conversations/{id}/messages"
        },
        "knowledge": {
            "list": "GET /api/v1/knowledge",
            "create": "POST /api/v1/knowledge",
            "query": "POST /api/v1/knowledge/query",
            "documents": "GET/POST /api/v1/knowledge/{id}/documents"
        },
        "models": {
            "list": "GET /api/v1/models",
            "detail": "GET /api/v1/models/{id}"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info" if not settings.DEBUG else "debug"
    )
