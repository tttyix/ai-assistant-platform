"""
对话模型
"""
from sqlalchemy import Column, String, DateTime, UUID, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base


class Conversation(Base):
    """
    对话模型
    存储用户与 AI 的对话会话信息
    """
    __tablename__ = "conversations"

    # 主键
    id = Column(UUID, primary_key=True, default=uuid.uuid4)

    # 外键
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)

    # 对话信息
    title = Column(String(255), nullable=False)
    model_id = Column(String(100), default="qwen-max")
    system_prompt = Column(String(1000), nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = Column(DateTime, nullable=True)

    # 关系
    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )

    def __repr__(self):
        return f"<Conversation {self.title}>"
