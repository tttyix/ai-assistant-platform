"""
工作流 API 路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

from ...services.workflow_engine import workflow_engine

router = APIRouter(prefix="/workflows", tags=["工作流"])


class WorkflowExecuteRequest(BaseModel):
    """工作流执行请求"""
    task: str = Field(..., description="任务描述（至少 10 个字符）", min_length=10, example="帮我创建一个 Python 计算器")
    mode: str = Field(default="aira+cc", description="执行模式：aira+cc（协作）| aira_only（仅分析）| cc_only（仅执行）", example="aira+cc")
    context: Optional[Dict] = Field(default=None, description="上下文信息（如技术栈、功能需求等）", example={"technologies": ["FastAPI", "PostgreSQL"]})


class WorkflowExecuteResponse(BaseModel):
    """工作流执行响应"""
    task_id: str = Field(..., description="任务唯一标识 ID", example="task_20260330143000")
    status: str = Field(..., description="执行状态：running | completed | failed", example="completed")
    summary: Optional[str] = Field(default=None, description="执行总结报告", example="✅ 任务执行完成！")
    error: Optional[str] = Field(default=None, description="错误信息（如果失败）", example=None)


@router.post("/execute", response_model=WorkflowExecuteResponse, summary="执行工作流任务", description="""
**执行 AI 协作任务**

通过工作流引擎协调 Aira（架构师）和 Claude Code（开发者）协作完成任务。

## 执行模式

- **aira+cc**: 协作模式 - Aira 分析 → CC 执行 → Aira 审查 → 总结
- **aira_only**: 仅分析 - Aira 分析需求并提供建议
- **cc_only**: 仅执行 - 直接调用 Claude Code 执行

## 返回结果

- **task_id**: 任务 ID，用于后续查询
- **status**: 执行状态（completed/failed）
- **summary**: 执行总结报告
- **error**: 错误信息（如果失败）

## 示例

```json
{
  "task": "帮我创建一个基于 FastAPI 的博客系统",
  "mode": "aira+cc",
  "context": {
    "features": ["用户认证", "文章管理", "评论系统"]
  }
}
```
""")
async def execute_workflow(request: WorkflowExecuteRequest):
    """执行工作流任务"""
    try:
        result = await workflow_engine.execute_task(
            task=request.task,
            mode=request.mode,
            context=request.context
        )
        
        return WorkflowExecuteResponse(
            task_id=result["task_id"],
            status=result["status"],
            summary=result.get("summary"),
            error=result.get("error")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=List[Dict], summary="查看任务历史", description="获取最近执行的工作流任务列表")
async def get_workflow_history(limit: int = 10):
    """
    获取工作流执行历史
    
    - **limit**: 返回最近 N 条记录（默认 10 条，最多 100 条）
    """
    return workflow_engine.get_task_history(limit=limit)


@router.get("/{task_id}", response_model=Dict, summary="查看任务详情", description="根据任务 ID 获取详细的执行信息")
async def get_workflow_task(task_id: str):
    """
    获取单个任务详情
    
    - **task_id**: 任务唯一标识
    """
    task = workflow_engine.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return task


@router.get("/templates", response_model=List[Dict], summary="查看可用模板", description="获取预定义的工作流模板列表")
async def get_workflow_templates():
    """
    获取工作流模板
    
    返回所有可用的工作流模板，包括：
    - 项目创建
    - 代码生成
    - 代码审查
    - Bug 修复
    - 文档编写
    """
    templates = [
        {
            "id": "project_creation",
            "name": "项目创建",
            "description": "创建完整的项目（后端/前端/全栈）",
            "mode": "aira+cc",
            "example": "帮我创建一个基于 FastAPI 的博客系统"
        },
        {
            "id": "code_generation",
            "name": "代码生成",
            "description": "生成特定功能的代码",
            "mode": "aira+cc",
            "example": "帮我写一个 Python 脚本来批量处理 Excel 文件"
        },
        {
            "id": "code_review",
            "name": "代码审查",
            "description": "审查和优化现有代码",
            "mode": "aira_only",
            "example": "帮我审查这个代码的质量和问题"
        },
        {
            "id": "bug_fix",
            "name": "Bug 修复",
            "description": "定位和修复 Bug",
            "mode": "aira+cc",
            "example": "这个代码报错了，帮我修复"
        },
        {
            "id": "documentation",
            "name": "文档编写",
            "description": "生成项目文档",
            "mode": "aira+cc",
            "example": "帮我为这个项目编写 README 文档"
        }
    ]
    
    return templates
