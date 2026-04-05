# Agent tests
import os
import sys

# 将项目根目录添加到 pythonpath
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent.factory import AgentFactory
from infrastructure.logging.manager import logger
from infrastructure.exceptions.handler import handle_exceptions

@handle_exceptions
def test_agent_basic_flow():
    """
    测试 Agent 的基本创建和工具调用流程
    """
    logger.info("开始 Agent 基础流程测试...")
    
    # 1. 创建 Agent (使用工厂模式)
    # 默认创建 ReAct Agent 并加载所有内置工具 (包括 get_current_time 和 knowledge_base_search)
    agent = AgentFactory.get_default_agent()
    
    # 2. 测试工具调用：询问时间
    # 预期：Agent 应该识别出需要调用 get_current_time 工具
    query_time = "帮我查一下现在几点了？"
    logger.info(f"测试查询 1: {query_time}")
    response_time = agent.run(query_time, session_id="test_user_1")
    print(f"\n[Agent 回答 - 时间]: {response_time['output']}")
    
    # 3. 测试知识库调用（如果知识库为空，模型应该返回友好提示）
    query_rag = "知识库里关于 Agent 配置的说明是什么？"
    logger.info(f"测试查询 2: {query_rag}")
    response_rag = agent.run(query_rag, session_id="test_user_1")
    print(f"\n[Agent 回答 - 知识库]: {response_rag['output']}")

    # 4. 测试记忆功能：追问
    query_memory = "我刚才问了你什么问题？"
    logger.info(f"测试查询 3 (记忆测试): {query_memory}")
    response_memory = agent.run(query_memory, session_id="test_user_1")
    print(f"\n[Agent 回答 - 记忆]: {response_memory['output']}")

if __name__ == '__main__':
    try:
        test_agent_basic_flow()
    except Exception as e:
        print(f"\n[测试失败]: {str(e)}")
        logger.error(f"Agent 测试过程中发生未捕获异常: {e}", exc_info=True)
