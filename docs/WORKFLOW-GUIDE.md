# 🤖 Aira + CC 协作功能使用指南

## ✅ 功能已实现

工作流引擎已经创建完成！现在你可以同时调用 **Aira（架构师）** 和 **Claude Code（开发者）** 来协作完成任务。

---

## 📋 API 端点

### 1. 执行工作流任务

```bash
POST /api/v1/workflows/execute
```

**请求体：**
```json
{
  "task": "帮我创建一个基于 FastAPI 的博客系统",
  "mode": "aira+cc",
  "context": {
    "technologies": ["FastAPI", "PostgreSQL"],
    "features": ["用户认证", "文章管理", "评论系统"]
  }
}
```

**响应：**
```json
{
  "task_id": "task_20260330142000",
  "status": "completed",
  "summary": "✅ 任务执行完成！\n\n## 执行概览\n- 任务 ID: task_20260330142000\n- 执行模式：aira+cc\n...",
  "error": null
}
```

---

## 🎯 执行模式

### 模式 1: `aira+cc`（协作模式）
```
流程：
1. Aira 分析需求 → 生成设计文档
2. Aira 调用 CC → 实现代码
3. Aira 审查代码 → 提出改进建议
4. CC 修改代码 → 完成实现
5. Aira 总结 → 回复用户
```

**适用场景：** 复杂项目、需要质量保证的任务

---

### 模式 2: `aira_only`（仅分析）
```
流程：
1. Aira 分析需求
2. Aira 生成建议
3. 返回分析报告
```

**适用场景：** 代码审查、技术咨询、方案设计

---

### 模式 3: `cc_only`（仅执行）
```
流程：
1. 直接调用 CC
2. CC 实现代码
3. 返回结果
```

**适用场景：** 简单任务、快速修改

---

## 📝 使用示例

### 示例 1：创建项目

```bash
curl -X POST "http://localhost:8000/api/v1/workflows/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "帮我创建一个待办事项管理系统",
    "mode": "aira+cc",
    "context": {
      "features": ["用户注册登录", "创建任务", "任务分类", "截止日期提醒"]
    }
  }'
```

---

### 示例 2：代码审查

```bash
curl -X POST "http://localhost:8000/api/v1/workflows/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "帮我审查这个代码的质量和问题：[粘贴代码]",
    "mode": "aira_only"
  }'
```

---

### 示例 3：Bug 修复

```bash
curl -X POST "http://localhost:8000/api/v1/workflows/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "这个 Python 脚本报错了：TypeError: expected str, bytes or os.PathLike object, not NoneType",
    "mode": "aira+cc"
  }'
```

---

## 🔍 查看任务历史

### 获取所有任务历史

```bash
GET /api/v1/workflows/history?limit=10
```

**响应：**
```json
[
  {
    "task_id": "task_20260330142000",
    "task": "帮我创建一个待办事项管理系统",
    "status": "completed",
    "started_at": "2026-03-30T14:20:00",
    "completed_at": "2026-03-30T14:25:00"
  }
]
```

---

### 获取单个任务详情

```bash
GET /api/v1/workflows/task_20260330142000
```

**响应：**
```json
{
  "task_id": "task_20260330142000",
  "task": "帮我创建一个待办事项管理系统",
  "mode": "aira+cc",
  "status": "completed",
  "steps": [
    {
      "step": 1,
      "name": "Aira 需求分析",
      "status": "completed",
      "result": {
        "task_type": "project_creation",
        "complexity": "medium",
        "estimated_files": 10
      }
    },
    {
      "step": 2,
      "name": "Claude Code 执行",
      "status": "completed",
      "result": {
        "success": true,
        "output": "✅ 已创建 10 个文件..."
      }
    },
    {
      "step": 3,
      "name": "Aira 代码审查",
      "status": "completed",
      "result": {
        "quality_score": 8.5,
        "needs_fix": false
      }
    },
    {
      "step": 4,
      "name": "Aira 总结",
      "status": "completed",
      "result": "✅ 任务执行完成！..."
    }
  ]
}
```

---

## 📋 工作流模板

### 获取所有模板

```bash
GET /api/v1/workflows/templates
```

**可用模板：**

| ID | 名称 | 模式 | 示例 |
|----|------|------|------|
| `project_creation` | 项目创建 | aira+cc | "帮我创建一个基于 FastAPI 的博客系统" |
| `code_generation` | 代码生成 | aira+cc | "帮我写一个 Python 脚本来批量处理 Excel 文件" |
| `code_review` | 代码审查 | aira_only | "帮我审查这个代码的质量和问题" |
| `bug_fix` | Bug 修复 | aira+cc | "这个代码报错了，帮我修复" |
| `documentation` | 文档编写 | aira+cc | "帮我为这个项目编写 README 文档" |

---

## 🎯 工作流程详解

### 协作模式（aira+cc）的完整流程

```
1️⃣ Aira 需求分析
   ├─ 任务分类（项目创建/修改/分析）
   ├─ 复杂度评估（简单/中等/复杂）
   ├─ 估算文件数
   ├─ 生成执行计划
   └─ 推荐技术栈

2️⃣ Claude Code 执行
   ├─ 接收 Aira 生成的提示词
   ├─ 创建项目结构
   ├─ 实现功能代码
   ├─ 添加注释和文档
   └─ 返回执行结果

3️⃣ Aira 代码审查
   ├─ 检查代码质量
   ├─ 评估完整性
   ├─ 识别潜在问题
   └─ 提出改进建议

4️⃣ Claude Code 修复（如需要）
   ├─ 根据 Aira 的建议修改
   ├─ 优化代码
   └─ 返回修复结果

5️⃣ Aira 总结
   ├─ 生成用户友好的报告
   ├─ 说明使用方法
   └─ 提供后续建议
```

---

## 🔧 配置选项

### 环境变量

在 `.env` 文件中配置：

```bash
# 工作流配置
WORKFLOW_TIMEOUT=600  # CC 执行超时（秒）
WORKSPACE_PATH=E:/ai-assistant-platform  # 工作目录

# CC 配置
CC_EXECUTABLE=claude  # CC CLI 命令
CC_PERMISSION_MODE=bypassPermissions  # 权限模式
```

---

## 📊 性能指标

| 指标 | 值 |
|------|-----|
| 简单任务耗时 | 1-3 分钟 |
| 中等任务耗时 | 3-10 分钟 |
| 复杂任务耗时 | 10-30 分钟 |
| CC 调用超时 | 10 分钟 |
| 任务历史保存 | 内存中（重启清除） |

---

## ⚠️ 注意事项

1. **CC 需要权限**
   - 确保 `claude` 命令可用
   - 使用 `--permission-mode bypassPermissions` 绕过权限检查

2. **超时设置**
   - 复杂任务可能超过 10 分钟
   - 可以调整 `WORKFLOW_TIMEOUT` 环境变量

3. **工作目录**
   - CC 会在工作目录创建文件
   - 确保有写入权限

4. **错误处理**
   - CC 执行失败会返回错误信息
   - Aira 会尝试分析和解释错误

---

## 🚀 快速测试

### 1. 访问 Swagger UI

```
http://localhost:8000/docs
```

找到 **工作流** 部分，点击 "Try it out" 测试。

### 2. 使用 curl 测试

```bash
curl -X POST "http://localhost:8000/api/v1/workflows/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "帮我创建一个简单的 Python 计算器",
    "mode": "aira+cc"
  }'
```

### 3. 查看结果

```bash
# 获取任务历史
curl "http://localhost:8000/api/v1/workflows/history"

# 获取任务详情（替换 task_id）
curl "http://localhost:8000/api/v1/workflows/{task_id}"
```

---

## 📝 下一步优化

1. **持久化存储** - 将任务历史保存到数据库
2. **实时日志** - WebSocket 推送执行进度
3. **文件预览** - 查看 CC 创建的文件内容
4. **交互式修改** - 用户可以直接修改 CC 生成的代码
5. **更多模板** - 添加预定义的工作流模板

---

**协作功能已就绪！现在就开始试试吧！** 🚀
