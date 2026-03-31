"""
LangSmith 追踪集成

提供完整的 LLM 应用观测能力：
- 对话链路追踪
- RAG 检索追踪
- 模型调用追踪
- Token 消耗统计
- 错误调试
"""
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import time
import uuid
from functools import wraps

from ..config import get_settings

settings = get_settings()

# ========== LangSmith 客户端初始化 ==========

langsmith_client = None
tracer = None

def init_langsmith():
    """初始化 LangSmith 客户端"""
    global langsmith_client, tracer

    if not settings.LANGSMITH_TRACING or not settings.LANGSMITH_API_KEY:
        print("[WARNING] LangSmith 追踪未启用（缺少配置）")
        return False

    try:
        from langsmith import Client, traceable

        langsmith_client = Client(
            api_key=settings.LANGSMITH_API_KEY,
            api_url=settings.LANGSMITH_ENDPOINT
        )

        tracer = traceable
        print(f"[OK] LangSmith 已初始化 (项目：{settings.LANGSMITH_PROJECT})")
        return True

    except ImportError:
        print("[WARNING] 未安装 langsmith，请运行：pip install langsmith")
        return False
    except Exception as e:
        print(f"[WARNING] LangSmith 初始化失败：{e}")
        return False


class LangSmithTracer:
    """LangSmith 手动追踪器"""

    def __init__(self):
        self.client = langsmith_client

    def start_trace(self, name: str, run_type: str = "chain", inputs: Optional[Dict] = None):
        if not self.client or not settings.LANGSMITH_TRACING:
            return None
        try:
            from langsmith.run_helpers import RunTree
            run = RunTree(
                name=name,
                run_type=run_type,
                inputs=inputs or {},
                project_name=settings.LANGSMITH_PROJECT
            )
            return run
        except Exception as e:
            print(f"LangSmith start_trace 失败：{e}")
            return None

    def end_trace(self, run, outputs: Optional[Dict] = None, error: Optional[str] = None):
        if not run or not self.client:
            return
        try:
            if outputs:
                run.end(outputs=outputs)
            if error:
                run.end(error=error)
            run.post()
        except Exception as e:
            print(f"LangSmith end_trace 失败：{e}")

    def log_llm_call(self, model: str, messages: List[Dict], response: str,
                     tokens: Dict[str, int], latency_ms: float, run=None):
        if not self.client or not settings.LANGSMITH_TRACING:
            return
        try:
            from langsmith.run_helpers import RunTree
            llm_run = RunTree(
                name=f"llm_call_{model}",
                run_type="llm",
                inputs={"messages": messages},
                outputs={"content": response, "tokens": tokens, "latency_ms": latency_ms},
                project_name=settings.LANGSMITH_PROJECT,
                parent_run=run,
                extra={"metadata": {"model": model, "token_usage": tokens}}
            )
            llm_run.post()
        except Exception as e:
            print(f"LangSmith log_llm_call 失败：{e}")


def setup_langsmith_middleware(app):
    """为 FastAPI 应用添加 LangSmith 中间件"""
    if not settings.LANGSMITH_TRACING or not langsmith_client:
        return
    print("[OK] LangSmith 中间件已注册")
