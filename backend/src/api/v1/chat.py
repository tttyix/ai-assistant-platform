"""
对话 API 路由
提供对话相关的 RESTful 接口
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
import time

from ... import database
from ...models.conversation import Conversation
from ...models.message import Message
from ...providers.base import ChatMessage, ChatRequest
from ...providers.model_registry import model_registry
from ...schemas.chat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ConversationCreate,
    ConversationResponse,
    MessageResponse,
)
from ...utils.langsmith_tracing import LangSmithTracer

router = APIRouter()


# ========== 对话接口 ==========

@router.post("/completions", response_model=ChatCompletionResponse)
async def create_completion(
    request: ChatCompletionRequest,
    db: Session = Depends(database.get_db)
):
    """创建对话完成"""
    start_time = time.time()
    tracer = LangSmithTracer()

    run = tracer.start_trace(
        name="chat_completion",
        run_type="chain",
        inputs={
            "model": request.model,
            "messages": request.messages,
            "conversation_id": request.conversation_id,
        }
    )

    try:
        chat_messages = [
            ChatMessage(role=msg["role"], content=msg["content"])
            for msg in request.messages
        ]

        chat_request = ChatRequest(
            messages=chat_messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )

        response = await model_registry.chat(chat_request)
        latency_ms = (time.time() - start_time) * 1000

        tracer.log_llm_call(
            model=request.model,
            messages=request.messages,
            response=response.content,
            tokens=response.tokens_used or {},
            latency_ms=latency_ms,
            run=run
        )

        if request.conversation_id:
            try:
                conversation_uuid = uuid.UUID(request.conversation_id)
                message = Message(
                    conversation_id=conversation_uuid,
                    role="assistant",
                    content=response.content,
                    model_id=request.model,
                    tokens_used=response.tokens_used.get("total_tokens", 0)
                )
                db.add(message)
                conversation = db.query(Conversation).filter(
                    Conversation.id == conversation_uuid
                ).first()
                if conversation:
                    conversation.last_message_at = datetime.utcnow()
                    conversation.updated_at = datetime.utcnow()
                db.commit()
            except (ValueError, Exception) as e:
                db.rollback()
                print(f"保存消息失败：{e}")

        tracer.end_trace(run=run, outputs={"content": response.content, "tokens": response.tokens_used})
        return response

    except ValueError as e:
        tracer.end_trace(run=run, error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        tracer.end_trace(run=run, error=str(e))
        raise HTTPException(status_code=500, detail=f"模型调用失败：{str(e)}")


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(database.get_db)
):
    """
    获取对话列表

    Args:
        skip: 跳过数量
        limit: 返回数量限制
        db: 数据库会话

    Returns:
        List[ConversationResponse]: 对话列表
    """
    conversations = (
        db.query(Conversation)
        .order_by(Conversation.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return conversations


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreate,
    db: Session = Depends(database.get_db)
):
    """
    创建新对话

    Args:
        request: 创建对话请求
        db: 数据库会话

    Returns:
        ConversationResponse: 创建的对话
    """
    conversation = Conversation(
        title=request.title,
        model_id=request.model_id or "qwen-max",
        system_prompt=request.system_prompt
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(database.get_db)
):
    """
    获取单个对话详情

    Args:
        conversation_id: 对话 ID
        db: 数据库会话

    Returns:
        ConversationResponse: 对话详情

    Raises:
        HTTPException: 当对话不存在时抛出
    """
    try:
        conversation_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的对话 ID")

    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_uuid
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")

    return conversation


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(database.get_db)
):
    """
    删除对话

    Args:
        conversation_id: 对话 ID
        db: 数据库会话

    Raises:
        HTTPException: 当对话不存在时抛出
    """
    try:
        conversation_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的对话 ID")

    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_uuid
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")

    db.delete(conversation)
    db.commit()

    return {"message": "对话已删除"}


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=List[MessageResponse]
)
async def list_messages(
    conversation_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db)
):
    """
    获取对话消息列表

    Args:
        conversation_id: 对话 ID
        skip: 跳过数量
        limit: 返回数量限制
        db: 数据库会话

    Returns:
        List[MessageResponse]: 消息列表

    Raises:
        HTTPException: 当对话不存在时抛出
    """
    try:
        conversation_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的对话 ID")

    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_uuid
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_uuid)
        .order_by(Message.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return messages
