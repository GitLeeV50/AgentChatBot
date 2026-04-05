# Tool registry
from typing import List, Any
from app.agent.tools.builtin import knowledge_base_search, get_current_time
# from app.agent.tools.custom import ...  # 导入用户自定义工具（如果有）
from infrastructure.logging.manager import logger

class ToolRegistry:
    """
    工具注册中心：负责收集并导出所有可用的工具对象
    """
    
    @staticmethod
    def get_langchain_tools() -> List[Any]:
        """
        获取所有已定义的 LangChain 工具对象列表
        """
        # 直接收集在 builtin.py 和 custom.py 中定义的工具实例
        # 注意：使用 @tool 装饰器后的函数本身就是一个 BaseTool 实例
        tools = [
            knowledge_base_search,
            get_current_time,

        ]
        
        logger.info(f"工具注册中心导出 {len(tools)} 个工具: {[t.name for t in tools]}")
        return tools
