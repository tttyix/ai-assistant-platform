"""
知识库 API 路由
提供知识库相关的 RESTful 接口
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from ... import database
from ...models.knowledge import KnowledgeBase, Document
from ...services.rag_service import RAGService
from ...schemas.knowledge import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    DocumentResponse,
    KnowledgeQuery,
    QueryResult,
)

router = APIRouter()
rag_service = RAGService()


# ========== 知识库接口 ==========

@router.post("/", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(
    request: KnowledgeBaseCreate,
    db: Session = Depends(database.get_db)
):
    """
    创建知识库

    Args:
        request: 创建知识库请求
        db: 数据库会话

    Returns:
        KnowledgeBaseResponse: 创建的知识库
    """
    knowledge_base = KnowledgeBase(
        name=request.name,
        description=request.description,
        is_public=request.is_public
    )

    db.add(knowledge_base)
    db.commit()
    db.refresh(knowledge_base)

    return knowledge_base


@router.get("/", response_model=List[KnowledgeBaseResponse])
async def list_knowledge_bases(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(database.get_db)
):
    """
    获取知识库列表

    Args:
        skip: 跳过数量
        limit: 返回数量限制
        db: 数据库会话

    Returns:
        List[KnowledgeBaseResponse]: 知识库列表
    """
    knowledge_bases = (
        db.query(KnowledgeBase)
        .order_by(KnowledgeBase.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return knowledge_bases


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: str,
    db: Session = Depends(database.get_db)
):
    """
    获取知识库详情

    Args:
        kb_id: 知识库 ID
        db: 数据库会话

    Returns:
        KnowledgeBaseResponse: 知识库详情

    Raises:
        HTTPException: 当知识库不存在时抛出
    """
    try:
        kb_uuid = uuid.UUID(kb_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的知识库 ID")

    knowledge_base = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_uuid
    ).first()

    if not knowledge_base:
        raise HTTPException(status_code=404, detail="知识库不存在")

    return knowledge_base


@router.put("/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    kb_id: str,
    request: KnowledgeBaseUpdate,
    db: Session = Depends(database.get_db)
):
    """
    更新知识库

    Args:
        kb_id: 知识库 ID
        request: 更新知识库请求
        db: 数据库会话

    Returns:
        KnowledgeBaseResponse: 更新后的知识库

    Raises:
        HTTPException: 当知识库不存在时抛出
    """
    try:
        kb_uuid = uuid.UUID(kb_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的知识库 ID")

    knowledge_base = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_uuid
    ).first()

    if not knowledge_base:
        raise HTTPException(status_code=404, detail="知识库不存在")

    # 更新字段
    if request.name is not None:
        knowledge_base.name = request.name
    if request.description is not None:
        knowledge_base.description = request.description
    if request.is_public is not None:
        knowledge_base.is_public = request.is_public

    knowledge_base.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(knowledge_base)

    return knowledge_base


@router.delete("/{kb_id}")
async def delete_knowledge_base(
    kb_id: str,
    db: Session = Depends(database.get_db)
):
    """
    删除知识库

    Args:
        kb_id: 知识库 ID
        db: 数据库会话

    Raises:
        HTTPException: 当知识库不存在时抛出
    """
    try:
        kb_uuid = uuid.UUID(kb_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的知识库 ID")

    knowledge_base = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_uuid
    ).first()

    if not knowledge_base:
        raise HTTPException(status_code=404, detail="知识库不存在")

    db.delete(knowledge_base)
    db.commit()

    return {"message": "知识库已删除"}


# ========== 文档接口 ==========

@router.get("/{kb_id}/documents", response_model=List[DocumentResponse])
async def list_documents(
    kb_id: str,
    db: Session = Depends(database.get_db)
):
    """
    获取知识库文档列表

    Args:
        kb_id: 知识库 ID
        db: 数据库会话

    Returns:
        List[DocumentResponse]: 文档列表

    Raises:
        HTTPException: 当知识库不存在时抛出
    """
    try:
        kb_uuid = uuid.UUID(kb_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的知识库 ID")

    knowledge_base = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_uuid
    ).first()

    if not knowledge_base:
        raise HTTPException(status_code=404, detail="知识库不存在")

    documents = db.query(Document).filter(
        Document.knowledge_base_id == kb_uuid
    ).all()

    return documents


@router.post("/{kb_id}/documents")
async def upload_document(
    kb_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    """
    上传文档到知识库

    Args:
        kb_id: 知识库 ID
        file: 上传的文件
        db: 数据库会话

    Returns:
        dict: 上传结果

    Raises:
        HTTPException: 当知识库不存在或文件类型不支持时抛出
    """
    try:
        kb_uuid = uuid.UUID(kb_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的知识库 ID")

    knowledge_base = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_uuid
    ).first()

    if not knowledge_base:
        raise HTTPException(status_code=404, detail="知识库不存在")

    # 检查文件类型
    allowed_types = [".txt", ".md", ".pdf", ".docx"]
    file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型，支持的类型：{', '.join(allowed_types)}"
        )

    # 创建文档记录
    document = Document(
        knowledge_base_id=kb_uuid,
        filename=file.filename,
        file_type=file_ext[1:],  # 移除前面的点
        status="pending"
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # TODO: 保存文件到存储
    # TODO: 异步处理文档（分块、向量化）
    # TODO: 存储到 Qdrant

    return {
        "message": "文档上传成功",
        "document_id": str(document.id),
        "filename": file.filename
    }


@router.delete("/{kb_id}/documents/{doc_id}")
async def delete_document(
    kb_id: str,
    doc_id: str,
    db: Session = Depends(database.get_db)
):
    """
    删除知识库文档

    Args:
        kb_id: 知识库 ID
        doc_id: 文档 ID
        db: 数据库会话

    Raises:
        HTTPException: 当知识库或文档不存在时抛出
    """
    try:
        kb_uuid = uuid.UUID(kb_id)
        doc_uuid = uuid.UUID(doc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的 ID")

    document = db.query(Document).filter(
        Document.id == doc_uuid,
        Document.knowledge_base_id == kb_uuid
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")

    db.delete(document)
    db.commit()

    return {"message": "文档已删除"}


# ========== 查询接口 ==========

@router.post("/query", response_model=List[QueryResult])
async def query_knowledge_base(
    request: KnowledgeQuery,
    kb_id: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    """
    查询知识库

    Args:
        request: 查询请求
        kb_id: 知识库 ID（可选）
        db: 数据库会话

    Returns:
        List[QueryResult]: 查询结果列表

    Raises:
        HTTPException: 当查询失败时抛出
    """
    try:
        results = await rag_service.query(
            question=request.question,
            knowledge_base_id=kb_id,
            top_k=request.top_k
        )

        return [
            QueryResult(
                text=result.get("text", ""),
                source=result.get("source", ""),
                score=result.get("score", 0.0)
            )
            for result in results
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败：{str(e)}")
