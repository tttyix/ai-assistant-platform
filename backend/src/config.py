"""
配置管理模块
管理应用的所有配置项，支持从环境变量加载
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类"""

    # ========== 应用配置 ==========
    APP_NAME: str = "AI 助手集成平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # ========== 数据库配置 ==========
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "ai_platform"
    POSTGRES_PASSWORD: str = "ai_platform_secret_2026"
    POSTGRES_DB: str = "ai_platform"

    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "ai_platform_redis_2026"

    # ========== 向量数据库配置 ==========
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "knowledge_base"

    # ========== 对象存储配置 ==========
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "ai_platform_minio"
    MINIO_SECRET_KEY: str = "ai_platform_minio_secret_2026"
    MINIO_BUCKET: str = "knowledge-base"

    # ========== AI 配置 ==========
    DASHSCOPE_API_KEY: str = "sk-sp-7350b52dc4d340e7b60703d4165c2971"
    DASHSCOPE_MODEL: str = "qwen-max"

    # 嵌入模型配置
    EMBEDDING_MODEL_PATH: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    # ========== 知识库配置 ==========
    KNOWLEDGE_BASE_PATH: str = "C:/Users/tttyi/knowledge-base"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 5

    # ========== JWT 配置 ==========
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ========== CORS 配置 ==========
    CORS_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置单例
    使用 lru_cache 确保配置只加载一次
    """
    return Settings()
