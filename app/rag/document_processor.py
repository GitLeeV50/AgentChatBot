# Document chunking processor
from typing import List, Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.rag.loaders.factory import LoaderFactory
from infrastructure.logging.manager import logger
from infrastructure.config.manager import conf_loader

class DocumentProcessor:
    """
    文档处理器：集成加载与分块逻辑
    """
    def __init__(self, 
                 chunk_size: Optional[int] = None, 
                 chunk_overlap: Optional[int] = None,
                 separators: Optional[List[str]] = None,
                 loader_factory: Optional[LoaderFactory] = None):
        
        # 优先从配置加载参数，否则使用默认值
        rag_config = conf_loader.get("rag", {}) if conf_loader else {}
        
        self.chunk_size = chunk_size or rag_config.get("chunk_size", 500)
        self.chunk_overlap = chunk_overlap or rag_config.get("chunk_overlap", 50)
        self.separators = separators or rag_config.get("separators", ["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""])
            
        self.loader_factory = loader_factory or LoaderFactory()
        
        # 初始化分块器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            length_function=len,
            add_start_index=True,
        )

    def process_directory(self, dir_path: Optional[str] = None, incremental: bool = True) -> List[Document]:
        """
        处理目录下所有文档：加载 -> 分块
        """
        # 如果未传入路径，尝试从配置读取
        if dir_path is None and conf_loader:
            dir_path = conf_loader.get("rag", {}).get("data_path", "data/external")
            
        if not dir_path:
            logger.error("未指定数据目录，且配置中也未找到 rag.data_path")
            return []

        logger.info(f"开始处理目录文档: {dir_path} (增量模式: {incremental})")
        
        # 1. 调用 Factory 加载原始文档
        raw_documents = self.loader_factory.load_directory(dir_path, incremental=incremental)
        
        if not raw_documents:
            logger.info("没有新文档需要处理")
            return []

        # 2. 执行分块
        logger.info(f"正在对 {len(raw_documents)} 个原始文档进行分块处理 (Size: {self.chunk_size}, Overlap: {self.chunk_overlap})...")
        chunks = self.text_splitter.split_documents(raw_documents)
        
        # 调试：检查分块内容
        for i, chunk in enumerate(chunks):
            logger.info(f"分块 {i}: 长度={len(chunk.page_content)}, 类型={type(chunk.page_content)}, 内容前50字符: {repr(chunk.page_content[:50])}")
        
        logger.info(f"分块处理完成，生成 {len(chunks)} 个分块")
        return chunks

    def process_documents(self, documents: List[Document]) -> List[Document]:
        """
        直接对传入的 Document 列表进行分块
        """
        if not documents:
            return []
            
        logger.info(f"正在对传入的 {len(documents)} 个文档进行分块...")
        return self.text_splitter.split_documents(documents)
