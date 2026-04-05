# Built-in tools
from langchain.tools import tool
from pydantic import BaseModel, Field
from app.rag.service import RAGService
from infrastructure.logging.manager import logger
from datetime import datetime
from utils.prompt_loader import load_role_prompts

# 实例化 RAG 服务供工具调用
rag_service = RAGService()

class RAGQueryInput(BaseModel):
    query: str = Field(description="需要从知识库中查询的具体问题")

@tool("knowledge_base_search", args_schema=RAGQueryInput)
def knowledge_base_search(query: str) -> str:
    """从专业知识库中搜索并总结答案。当你需要回答关于项目、文档、政策或特定领域知识的问题时使用此工具。"""
    try:
        logger.info(f"Agent 调用工具 [knowledge_base_search] 查询: {query}")
        # 调用已实现的 RAGService 进行问答
        response = rag_service.answer_question(query, print_prompt=True)
        return response
    except Exception as e:
        logger.error(f"工具 [knowledge_base_search] 执行失败: {e}")
        return f"知识库查询失败: {str(e)}"

@tool("get_current_time")
def get_current_time() -> str:
    """获取当前的日期和时间。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# @tool("inject_role_play")
# def inject_role_play() -> str:
#     """在需要角色扮演时注入 role_play 提示词。当用户输入任何跟男娘有关的词汇后调用，扮演小男娘。"""
#     try:
#         role_prompt = load_role_prompts()
#         return f"角色扮演模式激活：\n{role_prompt}"
#     except Exception as e:
#         return f"加载角色扮演提示失败: {str(e)}"
