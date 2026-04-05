# Custom tools (User extension point)
from app.agent.tools.base import tool
from infrastructure.logging.manager import logger


"""
在此文件中，用户可以根据业务需求自定义 Agent 工具。
只需使用 @tool 装饰器即可自动注册到工具中心。

示例：
@tool(
    name="my_custom_tool",
    description="这是一个自定义工具的描述"
)
def my_custom_tool(param: str) -> str:
    # 业务逻辑
    return f"Processed: {param}"
"""

# 您可以在这里开始编写您的自定义工具


