"""
数据库连接模块
提供 SQLAlchemy 数据库连接和会话管理
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import get_settings

settings = get_settings()

# 数据库 URL
DATABASE_URL = (
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

# 创建引擎
# pool_size: 连接池大小
# max_overflow: 连接池溢出时的最大连接数
# pool_pre_ping: 连接前测试，避免连接失效
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基础模型类
Base = declarative_base()


def get_db():
    """
    数据库会话依赖注入
    用于 FastAPI 路由的依赖项

    Yields:
        Session: SQLAlchemy 会话

    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库
    创建所有模型对应的表
    """
    Base.metadata.create_all(bind=engine)
    print("OK: 数据库表已创建")


def drop_db():
    """
    删除所有表
    仅在开发环境使用
    """
    Base.metadata.drop_all(bind=engine)
    print("🗑️ 数据库表已删除")
