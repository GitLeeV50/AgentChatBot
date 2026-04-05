# Loader factory
import os
import json
from typing import List, Dict, Type, Optional
from langchain_core.documents import Document
from app.rag.loaders.base import BaseDocumentLoader
from app.rag.loaders.implementations import PDFDocumentLoader, MarkdownDocumentLoader, TextDocumentLoader
from utils.file_handler import get_file_md5_hex
from infrastructure.logging.manager import logger
from infrastructure.exceptions.handler import FileIOError
from infrastructure.config.manager import conf_loader

class LoaderFactory:
    """
    加载器工厂，负责根据文件后缀获取对应加载器，并管理增量加载逻辑
    """
    
    # 扩展名与加载器映射
    LOADER_MAPPING: Dict[str, Type[BaseDocumentLoader]] = {
        ".pdf": PDFDocumentLoader,
        ".md": MarkdownDocumentLoader,
        ".txt": TextDocumentLoader
    }

    def __init__(self, state_file: Optional[str] = None):
        # 优先从配置获取状态文件路径
        rag_config = conf_loader.get("rag", {}) if conf_loader else {}
        self.state_file = state_file or rag_config.get("state_file", "data/processed_files.json")
        self.processed_files: Dict[str, str] = self._load_state()

    def _load_state(self) -> Dict[str, str]:
        """加载已处理文件的 MD5 状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载状态文件失败: {e}，将重新开始记录")
        return {}

    def _save_state(self):
        """保存已处理文件的 MD5 状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.processed_files, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存状态文件失败: {e}")

    def get_loader(self, file_path: str) -> Optional[BaseDocumentLoader]:
        """根据文件扩展名获取加载器实例"""
        _, ext = os.path.splitext(file_path)
        loader_cls = self.LOADER_MAPPING.get(ext.lower())
        if loader_cls:
            return loader_cls(file_path)
        return None

    def load_directory(self, dir_path: Optional[str] = None, incremental: bool = True) -> List[Document]:
        """
        加载目录下所有支持的文档
        
        :param dir_path: 目录路径（若为 None 则从配置读取）
        :param incremental: 是否增量加载
        :return: 加载到的 Document 列表
        """
        if dir_path is None and conf_loader:
            dir_path = conf_loader.get("rag", {}).get("data_path", "data/external")

        if not dir_path or not os.path.isdir(dir_path):
            raise FileIOError(f"目录不存在或未指定: {dir_path}", context={"path": dir_path})

        # 从配置读取允许的文件类型
        allow_types = [".txt", ".pdf", ".md"]
        if conf_loader:
            allow_types = conf_loader.get("rag", {}).get("allow_file_types", allow_types)

        all_documents = []
        new_processed_files = {} if not incremental else self.processed_files.copy()

        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            if not os.path.isfile(file_path):
                continue

            _, ext = os.path.splitext(filename)
            if ext.lower() not in allow_types:
                continue

            # 获取加载器
            loader = self.get_loader(file_path)
            if not loader:
                continue

            # MD5 校验
            try:
                current_md5 = get_file_md5_hex(file_path)
            except Exception as e:
                logger.error(f"计算文件 MD5 失败 {filename}: {e}")
                continue
            
            # 如果是增量加载且 MD5 未变，则跳过
            if incremental and file_path in self.processed_files:
                if self.processed_files[file_path] == current_md5:
                    logger.debug(f"文件未变化，跳过: {filename}")
                    continue

            # 执行加载
            try:
                logger.info(f"正在加载新文件/已更新文件: {filename}")
                docs = loader.load()
                all_documents.extend(docs)
                # 更新状态
                new_processed_files[file_path] = current_md5
            except Exception as e:
                logger.error(f"加载文件 {filename} 失败: {e}")

        # 更新并持久化状态
        self.processed_files = new_processed_files
        self._save_state()

        return all_documents
