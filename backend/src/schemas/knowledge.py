"""
知识库相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class KnowledgeBaseCreate(BaseModel):
    """创建知识库请求"""
    name: str = Field(..., description="知识库名称", min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, description="知识库描述")
    is_public: bool = Field(default=False, description="是否公开")


class KnowledgeBaseUpdate(BaseModel):
    """更新知识库请求"""
    name: Optional[str] = Field(default=None, description="知识库名称", min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, description="知识库描述")
    is_public: Optional[bool] = Field(default=None, description="是否公开")


class KnowledgeBaseResponse(BaseModel):
    """知识库响应"""
    id: str
    name: str
    description: Optional[str] = None
    document_count: int = 0
    vector_count: int = 0
    is_public: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    """文档响应"""
    id: str
    knowledge_base_id: str
    filename: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    chunk_count: int = 0
    status: str = "pending"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """文档上传响应"""
    message: str
    document_id: str
    filename: str


class KnowledgeQuery(BaseModel):
    """知识库查询请求"""
    question: str = Field(..., description="查询问题")
    knowledge_base_id: Optional[str] = Field(default=None, description="知识库 ID")
    top_k: int = Field(default=5, ge=1, le=20, description="返回结果数量")


class QueryResult(BaseModel):
    """查询结果"""
    text: str = Field(..., description="匹配文本")
    source: str = Field(..., description="来源")
    score: float = Field(..., description="相似度分数")
