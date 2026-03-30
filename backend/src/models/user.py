"""
用户模型
"""
from sqlalchemy import Column, String, DateTime, Boolean, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base


class User(Base):
    """
    用户模型
    存储用户基本信息和认证数据
    """
    __tablename__ = "users"

    # 主键
    id = Column(UUID, primary_key=True, default=uuid.uuid4)

    # 账户信息
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    api_key = Column(String(255), unique=True, index=True)

    # 角色和状态
    role = Column(String(50), default="user")  # admin, user, developer
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    # 关系
    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    knowledge_bases = relationship(
        "KnowledgeBase",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    workflows = relationship(
        "Workflow",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    usage_records = relationship(
        "UsageRecord",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"
