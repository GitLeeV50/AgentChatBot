# PDF/Markdown/TXT loader implementations
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, UnstructuredMarkdownLoader, TextLoader
from app.rag.loaders.base import BaseDocumentLoader
from infrastructure.exceptions.handler import FileIOError

class PDFDocumentLoader(BaseDocumentLoader):
    """
    PDF 加载器实现
    """
    def load(self) -> List[Document]:
        try:
            loader = PyPDFLoader(self.file_path)
            return loader.load()
        except Exception as e:
            raise FileIOError(f"PDF 加载失败: {str(e)}", context={"path": self.file_path})

class MarkdownDocumentLoader(BaseDocumentLoader):
    """
    Markdown 加载器实现
    """
    def load(self) -> List[Document]:
        try:
            loader = UnstructuredMarkdownLoader(self.file_path)
            return loader.load()
        except Exception as e:
            raise FileIOError(f"Markdown 加载失败: {str(e)}", context={"path": self.file_path})

class TextDocumentLoader(BaseDocumentLoader):
    """
    TXT 加载器实现
    """
    def load(self) -> List[Document]:
        try:
            loader = TextLoader(self.file_path, encoding="utf-8")
            return loader.load()
        except Exception as e:
            raise FileIOError(f"TXT 加载失败: {str(e)}", context={"path": self.file_path})
