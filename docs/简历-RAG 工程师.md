# 田逸旭

> 📧 邮箱：tttyixu9637@163.com  |  📱 手机：17265885407
> 💼 求职意向：RAG 工程师
> 🔗 GitHub: https://github.com/tttyix

---

## 🎓 教育背景

**[学校名称]**  |  **人工智能专业**  |  **本科**  |  2022.09 - 2026.06（预计）

- **主修课程**: Python 程序设计、数据结构、机器学习、深度学习、数据库原理

---

## 💻 专业技能

- **RAG 技术**：熟悉 RAG 检索增强系统，掌握文档加载、分块、向量化、检索全流程
- **向量数据库**：熟悉 FAISS、Qdrant，掌握 HNSW、IVF_PQ 等索引优化
- **混合检索**：熟悉 向量检索 + BM25 关键词检索融合策略，有 Rerank 重排序经验
- **知识图谱**：熟悉 Neo4j、Cypher 查询，有 GraphRAG 知识图谱检索经验
- **Linux/Shell**：熟悉 44 个核心命令，掌握 grep/cut/sort/uniq 文本处理，有 Shell 脚本编写经验
- **Embedding 模型**：熟悉 BGE-M3、sentence-transformers 等嵌入模型
- **编程语言**：Python (熟练), SQL (熟悉), JavaScript (熟悉)
- **后端开发**：FastAPI, SQLAlchemy, MySQL, PostgreSQL, Redis, RESTful API
- **工具框架**：LangChain, Git, Docker Compose, Linux, PyTorch, Transformers

---

### GraphRAG 全局搜索系统                              2025.11-2025.12
**项目角色**：RAG 系统开发工程师
**技术栈**：Microsoft GraphRAG, Neo4j, Leiden 算法

**项目描述**：
基于 Microsoft GraphRAG 构建知识图谱检索系统，支持跨文档全局推理。

**核心工作**：
- 基于 **Microsoft GraphRAG** 构建知识图谱检索系统
- 实现 **Leiden 社区发现算法**，生成层级化社区报告
- 设计 **Global Search 两阶段聚合流程**：Map 检索 → Reduce 汇总
- 配置 **Context Tokens 12,000**，Community Level 2 中等粒度

**技术成果**：
- 支持跨文档全局推理，回答复杂问题准确率提升 25%
- 社区报告自动生成，减少人工整理 80% 时间

---

## 🚀 项目经历

### AI 助手集成平台                                    2026.01-2026.03
**项目角色**：全栈开发 + RAG 系统开发
**技术栈**：LangChain, Qdrant, FastAPI, PostgreSQL, Redis

**项目描述**：
企业级 AI 助手平台，核心是基于 Qdrant 的 RAG 检索增强系统。

**核心工作**：
- 基于 **LangChain** 构建 RAG 检索增强系统：
  - **文档加载**：支持 PDF/Word/Markdown/TXT 四格式自动解析
  - **文本分块**：智能分块策略，500 字/块，重叠 50 字
  - **向量化**：sentence-transformers 嵌入模型，384 维 embedding
  - **存储**：Qdrant 向量数据库，HNSW 索引优化
- 实现 **混合检索策略**：向量相似度 (60%) + 关键词 BM25(40%) 加权融合
- 设计 **Rerank 重排序机制**，用 Cross-Encoder 对 Top-20 结果重新打分
- 优化检索性能：响应时间 < 200ms，召回率 92%
- 基于 **Qdrant payload 过滤**，支持知识库隔离与多租户

**技术成果**：
- 混合检索召回率 92%，Top-5 准确率 87%
- 语义检索响应 < 200ms，支持 4 种文档格式
- Rerank 重排序使准确率提升 15%
- 工作流自动化率 85%，复杂任务耗时 10-30 分钟
- 处理知识库文档 100+，50W+ tokens

---

### 医疗知识图谱问答系统                              2024.03-2024.06
**项目角色**：算法开发 + 知识图谱检索
**技术栈**：Neo4j, Cypher, BERT, PyTorch

**项目描述**：
基于知识图谱的医疗问答系统，探索 GraphRAG 知识图谱检索。

**核心工作**：
- 基于 **Neo4j** 构建医疗知识图谱：
  - 设计 12 类实体 Schema（疾病/症状/药品/检查/科室等）
  - 构建 50W+ 三元组，包含疾病关系、症状关系、治疗关系
  - 设计 Cypher 查询模板，支持 12 种意图的结构化查询
- 微调 **BERT 模型** 进行意图分类与 NER 实体抽取
- 实现语意解析流程：问题 → 意图 → 实体 → Cypher 生成 → 图谱查询
- 优化 **Cypher 查询性能**，复杂查询从 2s 降至 200ms

**技术成果**：
- 知识图谱 50W+ 三元组，12 类实体
- 意图识别准确率 91%，NER F1 值 0.88
- GraphRAG 检索响应 < 200ms
- 核心代码 3000+ 行，8 个模块

---

### AssistGen 智能客服助手                            2025.10-2025.12
**项目角色**：RAG 系统开发
**技术栈**：FAISS, BM25, FastAPI, MySQL, DeepSeek

**项目描述**：
智能客服系统，核心是 FAISS + BM25 双路检索的 RAG 系统。

**核心工作**：
- 构建 **RAG 检索增强系统**：
  - **向量化**：BGE-M3 嵌入模型，1024 维 embedding
  - **向量检索**：FAISS 索引，IVF_PQ 量化加速
  - **关键词检索**：BM25 算法，捕捉具体名词
  - **融合策略**：加权融合 (向量 60% + 关键词 40%)
- 实现 **Rerank 重排序**，用 Cross-Encoder 对 Top-20 重新打分
- 设计 **多策略分块**：语义分块 + 滑动窗口 + 结构分块
- 实现 **引用溯源**，每个答案标注来源文档与页码

**技术成果**：
- 多路检索融合策略，问答准确率提升 35%
- Rerank 重排序使 Top-5 准确率从 65% 提升到 87%
- 首 token 响应 < 500ms，P99 延迟 < 1.5s
- 支持 50+ 并发对话

---

## 📖 自我评价

- **RAG 全流程**：从文档加载、分块、向量化到检索、Rerank，均有实战经验
- **向量数据库**：FAISS、Qdrant 都有项目实践，了解 HNSW、IVF_PQ 等索引优化
- **混合检索**：多个项目实现向量 + 关键词双路检索，Rerank 使准确率提升 15-35%
- **知识图谱**：Neo4j 构建 50W+ 三元组，GraphRAG 实现 Leiden 社区发现与 Global Search
- **性能优化**：检索响应 < 200ms，有查询调优与索引优化经验
- **工程能力**：FastAPI 后端、Docker 部署、MySQL/PostgreSQL 数据库设计

---

## 💡 使用说明

### 1. 填写个人信息
替换 `[学校名称]` 为你的真实学校

### 2. 导出为 PDF
- **Typora**: 文件 → 导出 → PDF
- **VS Code**: 安装 "Markdown PDF" 插件，右键 → 导出
- **在线转换**: https://markdowntopdf.com/

### 3. 文件名建议
```
田逸旭_RAG 工程师_学校名称_17265885407.pdf
```

---

**祝求职顺利！拿到心仪的 Offer！** 🎉
