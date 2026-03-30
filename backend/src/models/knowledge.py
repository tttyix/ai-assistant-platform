"""
知识库模型
"""
from sqlalchemy import Column, String, DateTime, UUID, ForeignKey, Integer, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base


class KnowledgeBase(Base):
    """
    知识库模型
    存储用户创建的知识库信息
    """
    __tablename__ = "knowledge_bases"

    # 主键
    id = Column(UUID, primary_key=True, default=uuid.uuid4)

    # 外键
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)

    # 知识库信息
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # 统计信息
    document_count = Column(Integer, default=0)
    vector_count = Column(Integer, default=0)

    # 访问控制
    is_public = Column(Boolean, default=False)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="knowledge_bases")
    documents = relationship(
        "Document",
        back_populates="knowledge_base",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<KnowledgeBase {self.name}>"


class Document(Base):
    """
    文档模型
    存储知识库中的文档信息
    """
    __tablename__ = "documents"

    # 主键
    id = Column(UUID, primary_key=True, default=uuid.uuid4)

    # 外键
    knowledge_base_id = Column(UUID, ForeignKey("knowledge_bases.id"), nullable=False)

    # 文件信息
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)  # 字节
    file_type = Column(String(50), nullable=True)  # pdf, md, txt, docx

    # 处理信息
    chunk_count = Column(Integer, default=0)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed

    # 元数据
    extra_data = Column(JSON, nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")

    def __repr__(self):
        return f"<Document {self.filename}>"
