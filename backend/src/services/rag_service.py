"""
RAG 服务 - 检索增强生成 (Retrieval-Augmented Generation)

提供文档加载、分块、向量化存储和检索功能
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict, Optional
import torch

from ..config import get_settings

settings = get_settings()


class RAGService:
    """
    RAG 服务

    功能：
    1. 文档加载和分块
    2. 文本向量化
    3. 向量存储到 Qdrant
    4. 相似度检索
    """

    def __init__(self):
        """初始化 RAG 服务"""
        self.settings = get_settings()
        self.embeddings = None
        self.qdrant_client = None
        self.collection_name = self.settings.QDRANT_COLLECTION_NAME
        self.vector_size = 384  # paraphrase-multilingual-MiniLM-L12-v2 的输出维度

        self._init_embeddings()
        self._init_qdrant()

    def _init_embeddings(self):
        """
        初始化嵌入模型

        使用 HuggingFace 的 sentence-transformers 模型
        支持多语言（包括中文）
        """
        try:
            from langchain_huggingface import HuggingFaceEmbeddings

            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"正在加载嵌入模型 (设备：{device})...")

            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.settings.EMBEDDING_MODEL_PATH,
                model_kwargs={"device": device},
                encode_kwargs={"normalize_embeddings": True}
            )
            print("✅ 嵌入模型已加载")

        except ImportError:
            print("⚠️  未安装 langchain_huggingface，使用备用嵌入方案")
            self.embeddings = None
        except Exception as e:
            print(f"Warning: 嵌入模型加载失败：{e}")
            self.embeddings = None

    def _init_qdrant(self):
        """
        初始化 Qdrant 向量数据库客户端
        """
        try:
            self.qdrant_client = QdrantClient(
                host=self.settings.QDRANT_HOST,
                port=int(self.settings.QDRANT_PORT)
            )

            # 测试连接
            self.qdrant_client.get_collections()
            print("✅ Qdrant 客户端已连接")

            # 创建集合（如果不存在）
            self._create_collection_if_not_exists()

        except Exception as e:
            print(f"Warning: Qdrant 连接失败：{e}")
            self.qdrant_client = None

    def _create_collection_if_not_exists(self):
        """
        创建 Qdrant 集合（如果不存在）
        """
        if self.qdrant_client is None:
            return

        try:
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"✅ Qdrant 集合 '{self.collection_name}' 已创建")
            else:
                print(f"✅ Qdrant 集合 '{self.collection_name}' 已存在")

        except Exception as e:
            print(f"⚠️  创建 Qdrant 集合失败：{e}")

    def _embed_text(self, text: str) -> List[float]:
        """
        将文本转换为向量

        Args:
            text: 输入文本

        Returns:
            List[float]: 向量表示

        Raises:
            ValueError: 当嵌入模型未初始化时抛出
        """
        if self.embeddings is None:
            # 返回零向量作为备用方案
            return [0.0] * self.vector_size

        return self.embeddings.embed_query(text)

    def _split_text(
        self,
        text: str,
        chunk_size: int = None,
        chunk_overlap: int = None
    ) -> List[str]:
        """
        将文本分割成块

        Args:
            text: 输入文本
            chunk_size: 每块大小
            chunk_overlap: 块之间重叠

        Returns:
            List[str]: 文本块列表
        """
        chunk_size = chunk_size or self.settings.CHUNK_SIZE
        chunk_overlap = chunk_overlap or self.settings.CHUNK_OVERLAP

        # 简单实现：按字符分割
        # 生产环境应使用更复杂的分块策略（按句子、段落等）
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():  # 跳过空白块
                chunks.append(chunk.strip())
            start += chunk_size - chunk_overlap

        return chunks

    async def ingest_documents(
        self,
        file_paths: List[str],
        kb_id: Optional[str] = None
    ) -> int:
        """
        文档入库 - 加载、分块、向量化并存储

        Args:
            file_paths: 文件路径列表
            kb_id: 知识库 ID（可选）

        Returns:
            int: 处理的文本块数量

        Raises:
            ValueError: 当文件无法读取时抛出
        """
        if self.qdrant_client is None:
            raise ValueError("Qdrant 客户端未连接")

        all_chunks = []

        for path in file_paths:
            try:
                # 加载文档
                text = self._load_document(path)

                # 分块
                chunks = self._split_text(text)

                # 添加元数据
                for chunk in chunks:
                    all_chunks.append({
                        "text": chunk,
                        "source": path,
                        "kb_id": kb_id
                    })

            except Exception as e:
                print(f"⚠️  处理文件 {path} 失败：{e}")
                continue

        if not all_chunks:
            return 0

        # 向量化
        texts = [chunk["text"] for chunk in all_chunks]
        embeddings = [self._embed_text(text) for text in texts]

        # 构建点
        points = []
        for i, (chunk, embedding) in enumerate(zip(all_chunks, embeddings)):
            points.append(
                PointStruct(
                    id=i,
                    vector=embedding,
                    payload={
                        "text": chunk["text"],
                        "source": chunk["source"],
                        "kb_id": chunk["kb_id"]
                    }
                )
            )

        # 存储到 Qdrant
        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        print(f"✅ 已入库 {len(points)} 个文本块")
        return len(points)

    def _load_document(self, file_path: str) -> str:
        """
        加载文档内容

        Args:
            file_path: 文件路径

        Returns:
            str: 文档内容

        Raises:
            FileNotFoundError: 当文件不存在时抛出
            ValueError: 当文件类型不支持时抛出
        """
        import os

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在：{file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".txt":
            return self._load_text_file(file_path)
        elif ext == ".md":
            return self._load_markdown_file(file_path)
        elif ext == ".pdf":
            return self._load_pdf_file(file_path)
        elif ext == ".docx":
            return self._load_docx_file(file_path)
        else:
            raise ValueError(f"不支持的文件类型：{ext}")

    def _load_text_file(self, file_path: str) -> str:
        """加载纯文本文件"""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _load_markdown_file(self, file_path: str) -> str:
        """加载 Markdown 文件"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        # 简单清理 Markdown 语法
        import re
        # 移除代码块
        content = re.sub(r"```[\s\S]*?```", "", content)
        # 移除图片
        content = re.sub(r"!\[.*?\]\(.*?\)", "", content)
        # 移除链接但保留文本
        content = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", content)
        # 移除标题标记
        content = re.sub(r"^#+\s*", "", content, flags=re.MULTILINE)
        return content

    def _load_pdf_file(self, file_path: str) -> str:
        """加载 PDF 文件"""
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except ImportError:
            raise ValueError("未安装 pypdf，请运行：pip install pypdf")

    def _load_docx_file(self, file_path: str) -> str:
        """加载 DOCX 文件"""
        try:
            from docx import Document
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except ImportError:
            raise ValueError("未安装 python-docx，请运行：pip install python-docx")

    async def query(
        self,
        question: str,
        knowledge_base_id: Optional[str] = None,
        top_k: int = None
    ) -> List[Dict]:
        """
        查询知识库

        Args:
            question: 查询问题
            knowledge_base_id: 知识库 ID（可选）
            top_k: 返回结果数量

        Returns:
            List[Dict]: 查询结果列表，每项包含 text、source、score

        Raises:
            ValueError: 当 Qdrant 客户端未连接时抛出
        """
        if self.qdrant_client is None:
            raise ValueError("Qdrant 客户端未连接")

        top_k = top_k or self.settings.TOP_K

        # 向量化查询
        query_embedding = self._embed_text(question)

        # 构建过滤器
        query_filter = None
        if knowledge_base_id:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="kb_id",
                        match=MatchValue(value=knowledge_base_id)
                    )
                ]
            )

        # 搜索
        results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=query_filter,
            limit=top_k
        )

        # 格式化结果
        return [
            {
                "text": result.payload.get("text", ""),
                "source": result.payload.get("source", ""),
                "score": float(result.score)
            }
            for result in results
        ]

    async def ingest_text(
        self,
        text: str,
        source: str = "manual",
        kb_id: Optional[str] = None
    ) -> int:
        """
        直接摄入文本（无需文件）

        Args:
            text: 文本内容
            source: 来源标识
            kb_id: 知识库 ID（可选）

        Returns:
            int: 处理的文本块数量
        """
        if self.qdrant_client is None:
            raise ValueError("Qdrant 客户端未连接")

        # 分块
        chunks = self._split_text(text)

        if not chunks:
            return 0

        # 向量化
        embeddings = [self._embed_text(chunk) for chunk in chunks]

        # 构建点
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            points.append(
                PointStruct(
                    id=i,
                    vector=embedding,
                    payload={
                        "text": chunk,
                        "source": source,
                        "kb_id": kb_id
                    }
                )
            )

        # 存储到 Qdrant
        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        print(f"✅ 已入库 {len(points)} 个文本块")
        return len(points)
