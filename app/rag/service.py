# RAG service
from typing import List, Dict, Any, Optional
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.rag.vector_store import VectorStoreManager
from app.rag.document_processor import DocumentProcessor
from infrastructure.llm.client import get_llm_client
from infrastructure.logging.manager import logger
from utils.prompt_loader import load_rag_prompts

class RAGService:
    """
    RAG 业务封装类：整合加载、分块、存储和检索问答流程
    """
    def __init__(self):
        self.vector_store_manager = VectorStoreManager()
        self.document_processor = DocumentProcessor()
        self.llm_client = get_llm_client()
        
        # 加载提示词模板
        self.rag_prompt_template = load_rag_prompts()

    def update_knowledge_base(self, dir_path: Optional[str] = None, incremental: bool = True):
        """
        一键更新知识库：扫描目录 -> 加载 -> 分块 -> 存入向量库
        """
        logger.info("开始执行知识库全流程更新...")
        
        # 1. 加载并分块
        chunks = self.document_processor.process_directory(dir_path, incremental=incremental)
        
        if not chunks:
            logger.info("无新内容更新，跳过向量化步骤。")
            return
            
        # 2. 存入向量库
        self.vector_store_manager.add_documents(chunks)
        logger.info("知识库更新成功。")

    def _format_docs(self, docs):
        """格式化检索到的文档"""
        return "\n\n".join(doc.page_content for doc in docs)

    def answer_question(self, question: str, print_prompt: bool = True) -> str:
        """
        RAG 核心问答流程：检索 -> 注入 Prompt -> LLM 总结回答
        """
        logger.info(f"接收到 RAG 查询: {question}")
        
        # 1. 检索相关内容
        retriever = self.vector_store_manager.get_retriever()
        try:
            relevant_docs = retriever.invoke(question)
        except Exception as e:
            logger.error(f"向量库检索异常: {e}")
            return f"知识库检索失败: {str(e)}"
        
        # 2. 处理检索结果：如果未找到相关内容，直接告知
        if not relevant_docs:
            logger.warning(f"知识库检索未找到相关内容: {question}")
            return "抱歉，知识库中暂未找到与该问题相关的内容。"

        # 3. 过滤掉内容为空的文档
        valid_docs = [doc for doc in relevant_docs if doc.page_content and doc.page_content.strip()]
        if not valid_docs:
            logger.warning(f"知识库检索到的文档内容均为空: {question}")
            return "抱歉，检索到的相关文档内容为空，无法生成回答。"

        context = self._format_docs(valid_docs)
        
        # 4. 构造提示词
        prompt_template = PromptTemplate.from_template(self.rag_prompt_template)
        
        # 调试输出 Prompt
        if print_prompt:
            formatted_prompt = prompt_template.format(context=context, question=question)
            print("\n" + "="*50)
            print("--- DEBUG: RAG PROMPT ---")
            print(formatted_prompt)
            print("="*50 + "\n")

        # 5. 构建并执行 Chain
        model = self.llm_client.get_chat_model()
        
        try:
            # 确保输入字典包含 PromptTemplate 期望的所有变量
            inputs = {"context": context, "question": question}
            chain = prompt_template | model | StrOutputParser()
            response = chain.invoke(inputs)
            return response
        except Exception as e:
            logger.error(f"RAG 回答生成失败: {e}")
            # 增加对通义千问 400 错误的针对性提示
            if "400" in str(e) and "contents" in str(e):
                return "抱歉，由于检索到的内容格式不符合模型要求（可能包含非法字符或内容为空），无法生成回答。"
            return f"抱歉，知识库问答生成失败: {str(e)}"

    def get_raw_retriever(self):
        """暴露检索器，供 Agent 调用的 Tool 使用"""
        return self.vector_store_manager.get_retriever()
