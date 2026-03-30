"""
消息模型
"""
from sqlalchemy import Column, String, DateTime, UUID, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base


class Message(Base):
    """
    消息模型
    存储对话中的每条消息内容
    """
    __tablename__ = "messages"

    # 主键
    id = Column(UUID, primary_key=True, default=uuid.uuid4)

    # 外键
    conversation_id = Column(UUID, ForeignKey("conversations.id"), nullable=False)

    # 消息内容
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)

    # 模型信息
    model_id = Column(String(100), nullable=True)
    tokens_used = Column(Integer, default=0)
    cost = Column(JSON, nullable=True)  # {"input": 100, "output": 200}

    # 元数据
    extra_data = Column(JSON, nullable=True)  # 额外信息

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 关系
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message {self.id}>"
