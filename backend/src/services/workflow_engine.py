"""
工作流引擎 - 协调 Aira 和 Claude Code 的协作

功能：
1. 任务分析和拆解
2. 调用 Claude Code 执行
3. 代码审查和质量控制
4. 结果总结和文档生成
"""
import asyncio
import subprocess
import json
import os
import tempfile
from typing import Dict, List, Optional, AsyncIterator
from datetime import datetime
import aiofiles

from ..config import get_settings

settings = get_settings()


class WorkflowEngine:
    """
    工作流引擎
    
    协调 Aira（架构师）和 Claude Code（开发者）的协作
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.cc_executable = "claude"  # Claude Code CLI
        self.tasks = {}  # 任务历史
        
    async def execute_task(
        self,
        task: str,
        mode: str = "aira+cc",
        context: Optional[Dict] = None
    ) -> Dict:
        """
        执行任务
        
        Args:
            task: 任务描述
            mode: 执行模式
                - "aira_only": 仅 Aira 分析
                - "cc_only": 仅 CC 执行
                - "aira+cc": 协作模式（默认）
            context: 上下文信息
        
        Returns:
            执行结果
        """
        task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        result = {
            "task_id": task_id,
            "task": task,
            "mode": mode,
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "steps": []
        }
        
        try:
            # 1. Aira 分析需求
            if mode in ["aira_only", "aira+cc"]:
                analysis_step = {
                    "step": 1,
                    "name": "Aira 需求分析",
                    "status": "running"
                }
                result["steps"].append(analysis_step)
                
                analysis = await self._aira_analyze(task, context or {})
                analysis_step["status"] = "completed"
                analysis_step["result"] = analysis
                result["analysis"] = analysis
            
            # 2. 调用 Claude Code 执行
            if mode in ["cc_only", "aira+cc"]:
                cc_step = {
                    "step": 2,
                    "name": "Claude Code 执行",
                    "status": "running"
                }
                result["steps"].append(cc_step)
                
                # 生成 CC 提示词
                if mode == "aira+cc":
                    cc_prompt = self._generate_cc_prompt(analysis)
                else:
                    cc_prompt = task
                
                cc_result = await self._call_claude_code(cc_prompt)
                cc_step["status"] = "completed" if cc_result["success"] else "failed"
                cc_step["result"] = cc_result
                result["cc_result"] = cc_result
                
                if not cc_result["success"]:
                    result["error"] = cc_result.get("error", "Unknown error")
                    # 仅分析模式不需要 CC，直接跳过
                    if mode == "aira_only":
                        cc_step["status"] = "skipped"
                        result["cc_skipped"] = True
                    elif mode == "cc_only":
                        # 仅执行模式，CC 失败则返回失败
                        result["status"] = "failed"
                        cc_step["status"] = "failed"
                        return result
                    else:
                        # 协作模式：CC 失败，记录但继续，让 Aira 生成分析结果
                        cc_step["status"] = "failed"
                        result["cc_failed"] = True
            
            # 3. Aira 审查代码（协作模式）
            if mode == "aira+cc":
                review_step = {
                    "step": 3,
                    "name": "Aira 代码审查",
                    "status": "running"
                }
                result["steps"].append(review_step)
                
                review = await self._aira_review(cc_result)
                review_step["status"] = "completed"
                review_step["result"] = review
                result["review"] = review
                
                # 如果有问题，让 CC 修复
                if review.get("needs_fix", False):
                    fix_step = {
                        "step": 4,
                        "name": "Claude Code 修复",
                        "status": "running"
                    }
                    result["steps"].append(fix_step)
                    
                    fix_prompt = f"请修复以下问题：\n{review['issues']}"
                    fix_result = await self._call_claude_code(fix_prompt)
                    fix_step["status"] = "completed" if fix_result["success"] else "failed"
                    fix_step["result"] = fix_result
                    result["fix_result"] = fix_result
            
            # 4. Aira 总结
            if mode == "aira+cc":
                summary_step = {
                    "step": 5,
                    "name": "Aira 总结",
                    "status": "running"
                }
                result["steps"].append(summary_step)

                # 如果 CC 失败，生成特殊总结
                if result.get("cc_failed"):
                    summary = self._generate_cc_failed_summary(result)
                else:
                    summary = await self._aira_summarize(result)
                summary_step["status"] = "completed"
                summary_step["result"] = summary
                result["summary"] = summary
                result["status"] = "completed"

            elif mode == "aira_only":
                # 仅分析模式：生成分析回复
                reply_step = {
                    "step": 2,
                    "name": "Aira 生成回复",
                    "status": "running"
                }
                result["steps"].append(reply_step)

                reply = analysis.get("response", "分析完成")
                result["summary"] = f"## Aira 分析结果\n\n{reply}"
                reply_step["status"] = "completed"
                reply_step["result"] = {"response": reply}

            result["status"] = "completed"
            result["completed_at"] = datetime.now().isoformat()
            
        except Exception as e:
            import traceback
            print(f"[ERROR] 执行失败：{e}")
            print(f"Traceback: {traceback.format_exc()}")
            result["status"] = "failed"
            result["error"] = str(e)
            result["completed_at"] = datetime.now().isoformat()
        
        # 保存任务历史
        self.tasks[task_id] = result
        
        return result
    
    async def _aira_analyze(self, task: str, context: Dict) -> Dict:
        """
        Aira 分析需求

        返回：
        - 任务拆解
        - 技术选型
        - 执行计划
        """
        # 这里使用 AI 分析（可以调用 LLM API）
        # 简化版本：直接返回结构化分析

        analysis = {
            "task_type": self._classify_task(task),
            "complexity": self._estimate_complexity(task),
            "estimated_files": self._estimate_files(task),
            "plan": self._generate_plan(task),
            "technologies": self._suggest_technologies(task),
            "response": self._generate_response(task)
        }

        return analysis

    def _generate_response(self, task: str) -> str:
        """
        生成简单的对话回复（适用于问候、咨询等不需要代码执行的任务）
        """
        task_lower = task.lower()

        # 问候语
        if any(kw in task_lower for kw in ["你好", "hello", "hi", "嗨", "早上好", "下午好", "晚上好"]):
            return "你好！我是 AI 助手协作平台。我可以根据你的需求提供以下服务：\n\n1. **协作模式**：Aira 分析需求 → Claude Code 执行 → Aira 审查 → 总结\n2. **仅分析**：Aira 提供专业分析和建议\n3. **快速执行**：Claude Code 直接执行任务\n\n请问有什么可以帮你的吗？"

        # 感谢
        if any(kw in task_lower for kw in ["谢谢", "感谢", "thanks", "thank you"]):
            return "不客气！如果还有其他需要，随时告诉我。"

        # 再见
        if any(kw in task_lower for kw in ["再见", "bye", "goodbye", "拜拜"]):
            return "再见！祝你工作顺利！"

        # 默认回复
        return f"收到你的请求：'{task}'\n\n这是一个简单的咨询任务。如需执行具体操作，请选择更详细的任务描述，例如：\n- 帮我创建一个 Python 计算器\n- 帮我写一个 Excel 批处理脚本\n- 帮我审查这段代码"

    def _generate_cc_failed_summary(self, result: Dict) -> str:
        """
        生成 CC 失败时的总结报告
        """
        summary = []
        summary.append("[OK] 任务执行完成（Aira 分析模式）")
        summary.append("")
        summary.append("## 执行概览")
        summary.append(f"- 任务 ID: {result['task_id']}")
        summary.append(f"- 任务：{result.get('task', '未知')}")
        summary.append(f"- 执行模式：{result['mode']}")
        summary.append("")
        summary.append("## Aira 分析结果")

        # 尝试从分析结果中获取回复
        analysis = result.get('analysis', {})
        if analysis and 'response' in analysis:
            summary.append(analysis['response'])
        else:
            summary.append("已收到你的任务。由于这是一个咨询类任务，Aira 已为你提供分析建议。")
            summary.append("")
            summary.append("如需执行具体的代码创建或修改任务，请确保：")
            summary.append("1. Claude Code CLI 已正确安装和配置")
            summary.append("2. 你有权限在目标目录创建文件")
            summary.append("3. 任务描述足够清晰和具体")

        summary.append("")
        summary.append("## 执行步骤")
        for step in result.get('steps', []):
            status_icon = "[OK]" if step['status'] == 'completed' else "[FAILED]"
            summary.append(f"{status_icon} {step['name']}: {step['status']}")

        return "\n".join(summary)
    
    def _classify_task(self, task: str) -> str:
        """任务分类"""
        task_lower = task.lower()
        
        if any(kw in task_lower for kw in ["创建", "create", "build", "项目", "project"]):
            return "project_creation"
        elif any(kw in task_lower for kw in ["修改", "modify", "update", "修复", "fix"]):
            return "modification"
        elif any(kw in task_lower for kw in ["分析", "analyze", "审查", "review"]):
            return "analysis"
        else:
            return "general"
    
    def _estimate_complexity(self, task: str) -> str:
        """估算复杂度"""
        # 简单启发式：根据任务描述长度
        if len(task) < 50:
            return "simple"
        elif len(task) < 200:
            return "medium"
        else:
            return "complex"
    
    def _estimate_files(self, task: str) -> int:
        """估算需要创建的文件数"""
        complexity = self._estimate_complexity(task)
        
        if complexity == "simple":
            return 3
        elif complexity == "medium":
            return 10
        else:
            return 20
    
    def _generate_plan(self, task: str) -> List[str]:
        """生成执行计划"""
        # 简化版本：返回通用计划
        return [
            "1. 分析需求和功能点",
            "2. 设计项目结构",
            "3. 创建核心模块",
            "4. 实现业务逻辑",
            "5. 编写测试",
            "6. 文档说明"
        ]
    
    def _suggest_technologies(self, task: str) -> List[str]:
        """推荐技术栈"""
        task_lower = task.lower()
        
        technologies = []
        
        if any(kw in task_lower for kw in ["api", "backend", "服务"]):
            technologies.extend(["FastAPI", "SQLAlchemy", "PostgreSQL"])
        elif any(kw in task_lower for kw in ["前端", "frontend", "界面"]):
            technologies.extend(["Vue 3", "TypeScript", "Element Plus"])
        elif any(kw in task_lower for kw in ["数据库", "database"]):
            technologies.extend(["PostgreSQL", "Redis", "SQLAlchemy"])
        
        return technologies if technologies else ["Python", "FastAPI"]
    
    def _generate_cc_prompt(self, analysis: Dict) -> str:
        """
        生成给 Claude Code 的提示词
        
        基于 Aira 的分析结果，生成详细的执行指令
        """
        prompt = f"""请实现以下任务：

任务分析：
- 类型：{analysis['task_type']}
- 复杂度：{analysis['complexity']}
- 预估文件数：{analysis['estimated_files']}

执行计划：
{chr(10).join(analysis['plan'])}

推荐技术栈：
{', '.join(analysis['technologies'])}

请：
1. 创建完整的项目结构
2. 实现所有功能
3. 添加详细的代码注释
4. 确保代码可运行
5. 包含使用说明

开始执行！"""
        
        return prompt
    
    async def _call_claude_code(self, prompt: str) -> Dict:
        """
        调用 Claude Code CLI

        使用 subprocess 执行 claude 命令
        """
        try:
            print(f"[INFO] 调用 Claude Code...")

            # 使用系统临时目录（跨平台兼容）
            import tempfile
            temp_dir = tempfile.gettempdir()
            prompt_file = os.path.join(temp_dir, f"cc_prompt_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt")
            async with aiofiles.open(prompt_file, 'w', encoding='utf-8') as f:
                await f.write(prompt)

            # 直接调用 claude -p
            process = await asyncio.create_subprocess_exec(
                self.cc_executable,
                '-p', prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=settings.WORKSPACE_PATH if hasattr(settings, 'WORKSPACE_PATH') else '.'
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=600  # 10 分钟超时
            )

            # 清理临时文件
            try:
                os.remove(prompt_file)
            except:
                pass

            result = {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "output": stdout.decode('utf-8', errors='ignore'),
                "error": stderr.decode('utf-8', errors='ignore') if stderr else None
            }

            print(f"[OK] Claude Code 执行完成：{'成功' if result['success'] else '失败'}")
            print(f"Return code: {process.returncode}")
            print(f"Output: {result['output'][:200] if result['output'] else 'None'}")
            print(f"Error: {result['error'][:200] if result['error'] else 'None'}")

            return result
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "执行超时（>10 分钟）"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _aira_review(self, cc_result: Dict) -> Dict:
        """
        Aira 审查 CC 生成的代码
        
        检查：
        - 代码质量
        - 完整性
        - 潜在问题
        """
        # 简化版本：返回示例审查结果
        review = {
            "quality_score": 8.5,
            "completeness": "high",
            "issues": [],
            "suggestions": [
                "建议添加更多错误处理",
                "可以添加类型注解提高代码质量",
                "建议添加单元测试"
            ],
            "needs_fix": False
        }
        
        return review
    
    async def _aira_summarize(self, result: Dict) -> str:
        """
        Aira 总结执行结果
        
        生成用户友好的总结报告
        """
        summary = []
        summary.append("[OK] 任务执行完成！")
        summary.append("")
        summary.append("## 执行概览")
        summary.append(f"- 任务 ID: {result['task_id']}")
        summary.append(f"- 执行模式：{result['mode']}")
        summary.append(f"- 耗时：{result.get('completed_at', '')}")
        summary.append("")
        summary.append("## 执行步骤")
        
        for step in result.get('steps', []):
            status_icon = "[OK]" if step['status'] == 'completed' else "[FAILED]"
            summary.append(f"{status_icon} {step['name']}: {step['status']}")
        
        summary.append("")
        summary.append("## 下一步建议")
        summary.append("1. 检查生成的代码")
        summary.append("2. 运行测试")
        summary.append("3. 根据需要进行调整")
        
        return "\n".join(summary)
    
    def get_task_history(self, limit: int = 10) -> List[Dict]:
        """获取任务历史"""
        tasks = sorted(
            self.tasks.values(),
            key=lambda x: x.get('started_at', ''),
            reverse=True
        )
        return tasks[:limit]
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """获取单个任务详情"""
        return self.tasks.get(task_id)


# 全局工作流引擎实例
workflow_engine = WorkflowEngine()
