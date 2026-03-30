# 🤖 AI 助手集成平台

> 企业级 AI 助手集成平台 - 集成多模型对话、知识库 RAG、Aira+CC 协作工作流

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ 特性亮点

- 🤖 **多模型支持** - 集成通义千问、可扩展 OpenAI/Claude
- 📚 **知识库 RAG** - 基于 Qdrant 的语义检索
- ⚡ **工作流协作** - Aira（架构师）+ CC（开发者）协同工作
- 💻 **简洁界面** - 开箱即用的 Web UI
- 🐳 **Docker 部署** - 一键启动所有服务

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.12+
- Docker Desktop
- Node.js（可选，用于前端开发）

### 2. 克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/ai-assistant-platform.git
cd ai-assistant-platform
```

### 3. 启动 Docker 服务

```bash
docker-compose up -d
```

启动以下服务：
- PostgreSQL（数据库）
- Redis（缓存）
- Qdrant（向量数据库）
- MinIO（对象存储）

### 4. 安装 Python 依赖

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### 6. 启动后端服务

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. 访问应用

- **API 文档**: http://localhost:8000/docs
- **简洁界面**: 打开 `simple.html` 文件

---

## 💡 使用示例

### 方式 1：Web 界面（推荐）

打开 `simple.html` 文件，在浏览器中使用：

1. 输入任务描述
2. 选择执行模式
3. 点击执行

### 方式 2：API 调用

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/workflows/execute",
    json={
        "task": "帮我创建一个 Python 计算器",
        "mode": "aira+cc"
    }
)

print(response.json())
```

### 方式 3：PowerShell

```powershell
$body = @{
    task = "帮我写一个 Python 函数"
    mode = "aira+cc"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/execute" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

---

## 📋 核心功能

### 1. 💬 智能对话

- 多轮对话支持
- 对话历史管理
- 多模型切换

### 2. 📚 知识库 RAG

- 文档上传（Markdown/PDF/Word/TXT）
- 自动向量化
- 语义检索
- 引用溯源

### 3. ⚡ 工作流协作

**三种执行模式：**

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `aira+cc` | Aira 分析 + CC 执行 + Aira 审查 | 复杂项目 |
| `aira_only` | 仅 Aira 分析 | 代码审查、咨询 |
| `cc_only` | 仅 CC 执行 | 简单任务 |

**工作流程：**
```
用户任务
   ↓
Aira 需求分析（架构师）
   ↓
Claude Code 执行（开发者）
   ↓
Aira 代码审查（质量监督）
   ↓
总结报告
```

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────┐
│          Web UI / API Client            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         FastAPI 应用层                   │
│  ┌───────┬─────────┬─────────┬───────┐  │
│  │ 对话  │ 知识库  │  模型   │工作流 │  │
│  └───────┴─────────┴─────────┴───────┘  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           服务层                         │
│  ┌─────────────┬─────────────────────┐  │
│  │ RAG 服务     │  工作流引擎          │  │
│  └─────────────┴─────────────────────┘  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          数据存储层                      │
│  ┌──────┬──────┬────────┬──────────┐   │
│  │ PG   │Redis │ Qdrant │  MinIO   │   │
│  └──────┴──────┴────────┴──────────┘   │
└─────────────────────────────────────────┘
```

---

## 📁 项目结构

```
ai-assistant-platform/
├── backend/                    # 后端代码
│   ├── src/
│   │   ├── main.py            # FastAPI 入口
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   ├── models/            # 数据模型
│   │   ├── api/v1/            # API 路由
│   │   ├── services/          # 业务逻辑
│   │   ├── providers/         # AI 模型提供商
│   │   └── schemas/           # Pydantic 验证
│   ├── requirements.txt       # Python 依赖
│   ├── .env.example          # 环境变量示例
│   └── test-page.html        # 测试页面
├── docs/                      # 文档
│   ├── WORKFLOW-GUIDE.md     # 工作流指南
│   └── 中文使用指南.md        # 中文文档
├── scripts/                   # 脚本工具
│   ├── start-all.ps1         # 一键启动（Windows）
│   └── test-workflow.ps1     # 测试脚本
├── simple.html                # 简洁 Web 界面
├── docker-compose.yml         # Docker 编排
├── README.md                  # 项目说明
└── LICENSE                    # 许可证
```

---

## 🔧 配置说明

### 环境变量（.env）

```bash
# 数据库配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=ai_platform
POSTGRES_PASSWORD=your_password
POSTGRES_DB=ai_platform

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password

# Qdrant 配置
QDRANT_HOST=localhost
QDRANT_PORT=6333

# AI 配置
DASHSCOPE_API_KEY=your_api_key
DASHSCOPE_MODEL=qwen-max

# 知识库配置
KNOWLEDGE_BASE_PATH=/path/to/knowledge-base
```

---

## 🧪 测试

### 运行测试

```bash
cd backend
pytest
```

### API 测试

访问 http://localhost:8000/docs 使用 Swagger UI 测试所有接口。

---

## 📊 API 端点

### 对话接口
- `POST /api/v1/chat/completions` - 创建对话
- `GET /api/v1/chat/conversations` - 获取对话列表

### 知识库接口
- `POST /api/v1/knowledge/` - 创建知识库
- `POST /api/v1/knowledge/{id}/documents` - 上传文档
- `POST /api/v1/knowledge/query` - 查询知识库

### 工作流接口
- `POST /api/v1/workflows/execute` - 执行任务
- `GET /api/v1/workflows/history` - 查看历史
- `GET /api/v1/workflows/templates` - 查看模板

---

## 🐳 Docker 部署

### 启动所有服务

```bash
docker-compose up -d
```

### 查看状态

```bash
docker-compose ps
```

### 查看日志

```bash
docker-compose logs -f
```

### 停止服务

```bash
docker-compose down
```

---

## 🛠️ 开发指南

### 添加新的 AI 模型提供商

1. 在 `backend/src/providers/` 创建新文件
2. 继承 `BaseProvider` 类
3. 实现 `chat()` 和 `stream_chat()` 方法
4. 在 `model_registry.py` 中注册

### 添加新的 API 路由

1. 在 `backend/src/api/v1/` 创建新文件
2. 定义路由和 Schema
3. 在 `backend/src/main.py` 中注册

---

## 📝 常见问题

### Q: Docker 容器启动失败？

```bash
# 检查 Docker 状态
docker info

# 清理并重启
docker-compose down -v
docker-compose up -d
```

### Q: 端口冲突？

修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "8001:8000"  # 改为其他端口
```

### Q: API 密钥在哪里获取？

- **通义千问**: https://dashscope.console.aliyun.com/
- **OpenAI**: https://platform.openai.com/api-keys
- **Claude**: https://console.anthropic.com/

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代高性能 Web 框架
- [Qdrant](https://qdrant.tech/) - 向量数据库
- [LangChain](https://langchain.com/) - LLM 应用开发框架
- [Claude Code](https://claude.ai/) - AI 编程助手

---

## 📬 联系方式

- **项目主页**: https://github.com/YOUR_USERNAME/ai-assistant-platform
- **问题反馈**: https://github.com/YOUR_USERNAME/ai-assistant-platform/issues
- **邮箱**: your.email@example.com

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐ Star！**

Made with ❤️ by Aira + Claude Code

</div>
