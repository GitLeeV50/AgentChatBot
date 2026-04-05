# Agent factory
from typing import List, Optional
from infrastructure.llm.client import get_llm_client
from app.agent.tools.registry import ToolRegistry
from app.agent.core import ReActAgent, BaseAgent
from utils.prompt_loader import load_system_prompts
from infrastructure.logging.manager import logger

class AgentFactory:
    """
    智能体工厂：负责组装 LLM、工具和提示词，生产智能体实例
    """
    
    @staticmethod
    def create_agent(agent_type: str = "react", tool_names: Optional[List[str]] = None, model_name: Optional[str] = None, temperature: Optional[float] = None) -> BaseAgent:
        """
        根据类型创建智能体
        
        :param agent_type: 智能体类型 (目前仅支持 react)
        :param tool_names: 智能体可使用的工具列表，若为 None 则使用全部已注册工具
        :param model_name: 模型名称 (例如 qwen-max, gpt-4)
        :param temperature: 创造力参数
        """
        logger.info(f"正在创建类型为 {agent_type} 的智能体...")
        
        # 1. 获取 LLM
        llm = get_llm_client().get_chat_model(model_name=model_name, temperature=temperature)
        
        # 2. 获取工具
        tools = ToolRegistry.get_langchain_tools()
        if tool_names:
            tools = [t for t in tools if t.name in tool_names]
            
        # 3. 创建智能体实例
        if agent_type.lower() == "react":
            agent = ReActAgent(llm=llm, tools=tools)
            
            # 加载 ReAct 专用提示词
            prompt_template = load_system_prompts()
            
            # 构建执行器
            return agent.build(prompt_template)
        
        else:
            raise ValueError(f"暂不支持的智能体类型: {agent_type}")

    @staticmethod
    def get_default_agent() -> BaseAgent:
        """快速获取默认配置的智能体"""
        return AgentFactory.create_agent(agent_type="react")
