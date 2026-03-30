"""
多专家 Agent 系统 - Multi-Expert Agent System

实现类似 WorkBuddy 的多专家协作功能

专家角色列表：
- 营销专家 - 营销策略、品牌推广、用户增长
- 技术专家 - 架构设计、代码审查、技术选型
- 设计专家 - UI/UX 设计、配色方案、交互优化
- 数据专家 - 数据分析、指标解读、决策建议
- 产品专家 - 产品规划、需求分析、功能设计
- 运营专家 - 内容运营、活动策划、用户运营
"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class ExpertAgent(BaseModel):
    """专家 Agent 定义"""
    name: str = Field(..., description="专家名称")
    role: str = Field(..., description="角色定位")
    expertise: List[str] = Field(default_factory=list, description="专业领域")
    system_prompt: str = Field(..., description="系统提示词")
    icon: str = Field(default="👨‍💼", description="专家图标")


# 专家 Agent 配置
EXPERT_AGENTS = {
    "marketing": ExpertAgent(
        name="营销专家",
        role="营销策略与品牌推广专家",
        expertise=["营销策略", "品牌推广", "用户增长", "市场分析", "竞争分析"],
        system_prompt="""你是一位资深营销专家，拥有 10 年市场营销经验。
擅长制定营销策略、品牌推广方案、用户增长策略。
你的建议务实可行，注重 ROI 和数据驱动。""",
        icon="📈"
    ),
    
    "technical": ExpertAgent(
        name="技术专家",
        role="技术架构与开发专家",
        expertise=["架构设计", "代码审查", "技术选型", "性能优化", "安全"],
        system_prompt="""你是一位资深技术专家，拥有 10 年以上开发经验。
擅长系统架构设计、代码审查、技术选型。
你的建议注重可维护性、可扩展性和最佳实践。""",
        icon="💻"
    ),
    
    "design": ExpertAgent(
        name="设计专家",
        role="UI/UX 设计专家",
        expertise=["UI 设计", "UX 优化", "配色方案", "交互设计", "用户体验"],
        system_prompt="""你是一位资深设计师，拥有 10 年 UI/UX 设计经验。
擅长界面设计、用户体验优化、交互设计。
你的建议注重美观性、易用性和用户情感。""",
        icon="🎨"
    ),
    
    "data": ExpertAgent(
        name="数据专家",
        role="数据分析与决策专家",
        expertise=["数据分析", "指标解读", "A/B 测试", "数据可视化", "决策建议"],
        system_prompt="""你是一位资深数据分析师，拥有 10 年数据分析经验。
擅长从数据中发现问题、提供决策建议。
你的建议基于数据，注重可量化和可验证。""",
        icon="📊"
    ),
    
    "product": ExpertAgent(
        name="产品专家",
        role="产品规划与设计专家",
        expertise=["产品规划", "需求分析", "功能设计", "用户研究", "竞品分析"],
        system_prompt="""你是一位资深产品经理，拥有 10 年产品经验。
擅长产品规划、需求分析、功能设计。
你的建议注重用户需求、商业价值和技术可行性的平衡。""",
        icon="📱"
    ),
    
    "operation": ExpertAgent(
        name="运营专家",
        role="内容运营与活动策划专家",
        expertise=["内容运营", "活动策划", "用户运营", "社群运营", "转化率优化"],
        system_prompt="""你是一位资深运营专家，拥有 10 年运营经验。
擅长内容策划、活动运营、用户增长。
你的建议注重执行力、效果和用户参与度。""",
        icon="📢"
    ),
    
    "writing": ExpertAgent(
        name="写作专家",
        role="文档撰写与编辑专家",
        expertise=["文档写作", "文案润色", "内容总结", "公文写作", "创意写作"],
        system_prompt="""你是一位资深写作专家，拥有 10 年文字工作经验。
擅长各种文档撰写、文案润色、内容总结。
你的文字表达清晰、逻辑严谨、易于理解。""",
        icon="✍️"
    ),
    
    "translation": ExpertAgent(
        name="翻译专家",
        role="多语言翻译专家",
        expertise=["中英翻译", "日文翻译", "韩文翻译", "本地化", "跨文化交流"],
        system_prompt="""你是一位资深翻译专家，精通多国语言。
擅长准确传达原文意思，同时考虑文化差异。
你的翻译准确、流畅、符合目标语言习惯。""",
        icon="🌐"
    ),
    
    "ppt": ExpertAgent(
        name="PPT 专家",
        role="演示文稿设计专家",
        expertise=["PPT 设计", "演示结构", "视觉呈现", "演讲技巧", "信息图表"],
        system_prompt="""你是一位资深 PPT 设计师，拥有 10 年演示文稿设计经验。
擅长信息结构化、视觉呈现、演讲逻辑。
你的建议注重简洁、美观、有说服力。""",
        icon="📊"
    ),
    
    "meeting": ExpertAgent(
        name="会议专家",
        role="会议管理与纪要专家",
        expertise=["会议组织", "纪要整理", "议程设计", "决策跟踪", "效率提升"],
        system_prompt="""你是一位资深会议专家，拥有 10 年会议管理经验。
擅长高效会议组织、纪要整理、决策跟踪。
你的建议注重效率、结果导向、可执行。""",
        icon="🤝"
    )
}


class ExpertConsultationRequest(BaseModel):
    """专家咨询请求"""
    task: str = Field(..., description="任务描述")
    selected_experts: List[str] = Field(default_factory=list, description="选中的专家 ID 列表")
    mode: str = Field(default="sequential", description="执行模式：sequential（顺序）| parallel（并行）| discussion（讨论）")


class ExpertResponse(BaseModel):
    """专家回复"""
    expert_id: str
    expert_name: str
    icon: str
    response: str
    suggestions: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, description="信心指数 0-1")


class MultiExpertResult(BaseModel):
    """多专家咨询结果"""
    task: str
    experts_consulted: List[str]
    responses: List[ExpertResponse]
    summary: str
    action_items: List[str] = Field(default_factory=list)


class MultiExpertSystem:
    """
    多专家系统
    
    类似 WorkBuddy 的多 Agent 协作功能
    
    使用方式：
    1. 用户提出问题
    2. 选择一个或多个专家
    3. 各专家提供专业意见
    4. 整合所有意见，生成最终建议
    """
    
    def __init__(self):
        self.experts = EXPERT_AGENTS
    
    def get_available_experts(self) -> List[Dict]:
        """获取所有可用专家"""
        return [
            {
                "id": expert_id,
                "name": expert.name,
                "role": expert.role,
                "expertise": expert.expertise,
                "icon": expert.icon
            }
            for expert_id, expert in self.experts.items()
        ]
    
    async def consult_experts(
        self,
        task: str,
        selected_experts: List[str],
        mode: str = "sequential"
    ) -> MultiExpertResult:
        """
        咨询多个专家
        
        Args:
            task: 任务描述
            selected_experts: 选中的专家 ID 列表
            mode: 执行模式
                - sequential: 顺序执行（一个接一个）
                - parallel: 并行执行（同时咨询）
                - discussion: 讨论模式（专家之间互相讨论）
        
        Returns:
            多专家咨询结果
        """
        responses = []
        
        # 根据模式执行
        if mode == "sequential":
            # 顺序执行：每个专家依次回答
            for expert_id in selected_experts:
                if expert_id in self.experts:
                    response = await self._consult_single_expert(expert_id, task)
                    responses.append(response)
        
        elif mode == "parallel":
            # 并行执行：同时咨询所有专家（需要异步并发）
            import asyncio
            tasks = [
                self._consult_single_expert(expert_id, task)
                for expert_id in selected_experts
                if expert_id in self.experts
            ]
            responses = await asyncio.gather(*tasks)
        
        elif mode == "discussion":
            # 讨论模式：专家之间互相讨论（多轮对话）
            responses = await self._expert_discussion(task, selected_experts)
        
        # 整合结果
        summary = self._generate_summary(task, responses)
        action_items = self._extract_action_items(responses)
        
        return MultiExpertResult(
            task=task,
            experts_consulted=selected_experts,
            responses=responses,
            summary=summary,
            action_items=action_items
        )
    
    async def _consult_single_expert(
        self,
        expert_id: str,
        task: str
    ) -> ExpertResponse:
        """咨询单个专家"""
        expert = self.experts[expert_id]
        
        # 构建提示词
        prompt = f"""{expert.system_prompt}

请针对以下问题，从你的专业角度提供建议：

{task}

请按照以下格式回答：
1. 核心观点（1-2 句话）
2. 详细建议（3-5 点）
3. 注意事项
4. 推荐行动步骤"""

        # 调用 LLM（这里需要集成到你的 LLM 调用逻辑）
        # response = await call_llm(prompt, system_prompt=expert.system_prompt)
        
        # 临时返回示例回复
        return ExpertResponse(
            expert_id=expert_id,
            expert_name=expert.name,
            icon=expert.icon,
            response=f"[{expert.name}的专业建议]",
            suggestions=[
                "建议 1",
                "建议 2",
                "建议 3"
            ],
            confidence=0.85
        )
    
    async def _expert_discussion(
        self,
        task: str,
        selected_experts: List[str]
    ) -> List[ExpertResponse]:
        """专家讨论模式 - 多轮对话"""
        responses = []
        discussion_history = []
        
        # 第 1 轮：每个专家发表初始观点
        for expert_id in selected_experts:
            if expert_id in self.experts:
                response = await self._consult_single_expert(expert_id, task)
                responses.append(response)
                discussion_history.append(f"{response.expert_name}: {response.response}")
        
        # 第 2 轮：专家互相评论和补充
        # （可以实现更复杂的讨论逻辑）
        
        return responses
    
    def _generate_summary(
        self,
        task: str,
        responses: List[ExpertResponse]
    ) -> str:
        """生成总结"""
        summary_parts = ["## 专家咨询总结\n"]
        
        for response in responses:
            summary_parts.append(f"\n### {response.icon} {response.expert_name}")
            summary_parts.append(response.response)
        
        summary_parts.append("\n\n## 综合建议")
        summary_parts.append("综合各位专家的意见，建议按以下步骤行动：")
        
        return "\n".join(summary_parts)
    
    def _extract_action_items(
        self,
        responses: List[ExpertResponse]
    ) -> List[str]:
        """提取行动项"""
        action_items = []
        
        for response in responses:
            action_items.extend(response.suggestions)
        
        return action_items[:10]  # 最多返回 10 个行动项


# 全局实例
multi_expert_system = MultiExpertSystem()
