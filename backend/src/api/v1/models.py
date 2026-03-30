"""
模型 API 路由
提供模型列表和模型信息接口
"""
from fastapi import APIRouter, Depends
from typing import List

from ...providers.model_registry import model_registry
from ...providers.base import ModelInfo

router = APIRouter()


@router.get("/", response_model=List[ModelInfo])
async def list_models():
    """
    获取所有可用模型列表

    Returns:
        List[ModelInfo]: 模型信息列表
    """
    return model_registry.get_all_models()


@router.get("/{model_id}", response_model=ModelInfo)
async def get_model(model_id: str):
    """
    获取单个模型信息

    Args:
        model_id: 模型 ID

    Returns:
        ModelInfo: 模型信息

    Raises:
        HTTPException: 当模型不存在时抛出
    """
    models = model_registry.get_all_models()
    for model in models:
        if model.id == model_id:
            return model

    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail=f"模型 {model_id} 不存在")
