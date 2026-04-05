# Vector store management
import os
from typing import List, Optional
from langchain_chroma import Chroma
from langchain_core.documents import Document
from infrastructure.llm.client import get_llm_client
from infrastructure.config.manager import conf_loader
from infrastructure.logging.manager import logger
from infrastructure.exceptions.handler import RAGError

class VectorStoreManager:
    """
    向量库管理器：负责初始化向量库、向量化存储以及检索
    """
    def __init__(self, 
                 collection_name: Optional[str] = None, 
                 persist_directory: Optional[str] = None):
        
        # 1. 加载配置
        rag_config = conf_loader.get("rag", {}) if conf_loader else {}
        self.collection_name = collection_name or rag_config.get("collection_name", "agent_knowledge")
        self.persist_directory = persist_directory or rag_config.get("persist_directory", "data/chroma_db")
        self.top_k = rag_config.get("top_k", 3)

        # 2. 获取 Embedding 模型
        try:
            self.embeddings = get_llm_client().get_embedding_model()
        except Exception as e:
            raise RAGError(f"获取 Embedding 模型失败: {str(e)}")

        # 3. 初始化 Chroma 向量库
        self.vector_store = self._init_vector_store()

    def _init_vector_store(self) -> Chroma:
        """初始化或加载现有的向量库"""
        try:
            # 确保持久化目录存在
            os.makedirs(self.persist_directory, exist_ok=True)
            
            return Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
        except Exception as e:
            raise RAGError(f"初始化向量库失败: {str(e)}", context={"persist_directory": self.persist_directory})

    def add_documents(self, documents: List[Document]):
        """
        将文档向量化并存入库中
        """
        if not documents:
            logger.info("没有文档需要存入向量库")
            return

        # 调试：检查文档结构
        for i, doc in enumerate(documents):
            logger.info(f"文档 {i}: page_content 类型={type(doc.page_content)}, 长度={len(doc.page_content)}, metadata={doc.metadata}")

        try:
            logger.info(f"正在将 {len(documents)} 个分块存入向量库...")
            self.vector_store.add_documents(documents)
            logger.info("向量化存储完成")
        except Exception as e:
            raise RAGError(f"文档存入向量库失败: {str(e)}")

    def get_retriever(self, search_kwargs: Optional[dict] = None):
        """
        返回 LangChain 检索器对象
        """
        kwargs = search_kwargs or {"k": self.top_k}
        return self.vector_store.as_retriever(search_kwargs=kwargs)

    def similarity_search(self, query: str, k: Optional[int] = None) -> List[Document]:
        """
        执行相似度搜索
        """
        try:
            search_k = k or self.top_k
            return self.vector_store.similarity_search(query, k=search_k)
        except Exception as e:
            logger.error(f"相似度搜索失败: {e}")
            return []

    def clear_collection(self):
        """
        清空当前集合的所有数据
        """
        try:
            self.vector_store.delete_collection()
            self.vector_store = self._init_vector_store()
            logger.info(f"已清空向量库集合: {self.collection_name}")
        except Exception as e:
            raise RAGError(f"清空向量库失败: {str(e)}")
