"""
对话相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class ChatMessage(BaseModel):
    """对话消息"""
    role: str = Field(..., description="消息角色", examples=["user", "assistant", "system"])
    content: str = Field(..., description="消息内容")


class ChatCompletionRequest(BaseModel):
    """对话完成请求"""
    messages: List[Dict[str, str]] = Field(..., description="消息列表")
    model: str = Field(default="qwen-max", description="模型 ID")
    temperature: float = Field(default=0.7, ge=0, le=2, description="温度参数")
    max_tokens: int = Field(default=2048, ge=1, le=100000, description="最大生成 token 数")
    stream: bool = Field(default=False, description="是否流式输出")
    conversation_id: Optional[str] = Field(default=None, description="对话 ID")


class ChatCompletionResponse(BaseModel):
    """对话完成响应"""
    content: str = Field(..., description="回复内容")
    model: str = Field(..., description="使用的模型")
    tokens_used: Dict[str, int] = Field(..., description="Token 使用统计")
    finish_reason: str = Field(..., description="结束原因")


class ConversationCreate(BaseModel):
    """创建对话请求"""
    title: str = Field(..., description="对话标题", min_length=1, max_length=255)
    model_id: Optional[str] = Field(default="qwen-max", description="模型 ID")
    system_prompt: Optional[str] = Field(default=None, description="系统提示词")


class ConversationResponse(BaseModel):
    """对话响应"""
    id: str
    title: str
    model_id: str
    system_prompt: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """消息响应"""
    id: str
    role: str
    content: str
    model_id: Optional[str] = None
    tokens_used: int = 0
    created_at: datetime

    class Config:
        from_attributes = True
