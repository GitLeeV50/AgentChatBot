# RAG tests
import os
import sys

# 将项目根目录添加到 pythonpath
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from app.rag.service import RAGService
from infrastructure.logging.manager import logger
from infrastructure.exceptions.handler import handle_exceptions


@handle_exceptions
def test_rag_answer_question():
    """
    测试 RAG 服务的 answer_question 方法
    输入：我体重180斤，尺码推荐
    """
    logger.info("开始 RAG 问答测试...")

    # 1. 创建 RAG 服务实例
    rag_service = RAGService()

    # 2. 清空向量库并重新更新知识库
    logger.info("清空向量库...")
    rag_service.vector_store_manager.clear_collection()
    
    logger.info("更新知识库...")
    rag_service.update_knowledge_base(incremental=False)  # 强制重新加载所有文档

    # 3. 测试输入
    query = "我体重180斤，尺码推荐"
    logger.info(f"测试查询: {query}")

    # 4. 调用 RAG 问答
    response = rag_service.answer_question(query)

    # 5. 输出结果
    print(f"\n[RAG 回答]: {response}")

    # 6. 基本断言：确保返回的是字符串且不为空
    assert isinstance(response, str), "响应应该是一个字符串"
    assert len(response.strip()) > 0, "响应不应该为空"

    logger.info("RAG 问答测试完成。")


if __name__ == "__main__":
    try:
        test_rag_answer_question()
    except Exception as e:
        print(f"\n[测试失败]: {str(e)}")
        logger.error(f"RAG 测试过程中发生未捕获异常: {e}", exc_info=True)
