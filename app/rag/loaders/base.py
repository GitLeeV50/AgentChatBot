# Loader base classes
from abc import ABC, abstractmethod
from typing import List
from langchain_core.documents import Document

class BaseDocumentLoader(ABC):
    """
    文档加载器基类
    """
    def __init__(self, file_path: str):
        self.file_path = file_path

    @abstractmethod
    def load(self) -> List[Document]:
        """
        加载文档并返回 Document 对象列表
        """
        pass
