# Callback handlers for monitoring and logging
import time
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from infrastructure.logging.manager import logger, llm_logger, error_logger

class AgentBotCallbackHandler(BaseCallbackHandler):
    """
    AgentBot 统一回调处理器：监控 LLM 调用和工具执行
    """
    
    def __init__(self):
        self.start_time: Dict[str, float] = {}

    # --- LLM 监控 ---
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], *, run_id: UUID, **kwargs: Any
    ) -> None:
        """LLM 开始调用"""
        self.start_time[str(run_id)] = time.time()
        llm_logger.info(f"--- LLM START [Run ID: {run_id}] ---")
        for i, prompt in enumerate(prompts):
            llm_logger.debug(f"Prompt {i}: {prompt}")

    def on_llm_end(self, response: LLMResult, *, run_id: UUID, **kwargs: Any) -> None:
        """LLM 调用结束"""
        duration = time.time() - self.start_time.get(str(run_id), 0)
        llm_logger.info(f"--- LLM END [Run ID: {run_id}] | Duration: {duration:.2f}s ---")
        
        # 记录 Token 使用情况 (如果提供商支持)
        if response.llm_output and "token_usage" in response.llm_output:
            usage = response.llm_output["token_usage"]
            llm_logger.info(f"Token Usage: {usage}")

        for i, generations in enumerate(response.generations):
            for j, generation in enumerate(generations):
                llm_logger.debug(f"Generation {i}-{j}: {generation.text}")

    def on_llm_error(self, error: Union[Exception, KeyboardInterrupt], *, run_id: UUID, **kwargs: Any) -> None:
        """LLM 调用出错"""
        error_logger.error(f"LLM Error [Run ID: {run_id}]: {str(error)}", exc_info=True)

    # --- Tool 监控 ---
    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, *, run_id: UUID, **kwargs: Any
    ) -> None:
        """工具开始执行"""
        self.start_time[str(run_id)] = time.time()
        tool_name = serialized.get("name", "Unknown Tool")
        logger.info(f"--- TOOL START: {tool_name} [Run ID: {run_id}] ---")
        logger.debug(f"Tool Input: {input_str}")

    def on_tool_end(self, output: str, *, run_id: UUID, **kwargs: Any) -> None:
        """工具执行结束"""
        duration = time.time() - self.start_time.get(str(run_id), 0)
        logger.info(f"--- TOOL END | Duration: {duration:.2f}s ---")
        logger.debug(f"Tool Output: {output}")

    def on_tool_error(self, error: Union[Exception, KeyboardInterrupt], *, run_id: UUID, **kwargs: Any) -> None:
        """工具执行出错"""
        error_logger.error(f"Tool Error [Run ID: {run_id}]: {str(error)}", exc_info=True)

    # --- Agent 监控 ---
    def on_agent_action(self, action: Any, *, run_id: UUID, **kwargs: Any) -> None:
        """Agent 决定采取行动"""
        logger.info(f"Agent Action: {action.tool} | Thought: {action.log}")

    def on_agent_finish(self, finish: Any, *, run_id: UUID, **kwargs: Any) -> None:
        """Agent 执行完成"""
        logger.info(f"Agent Finished: {finish.return_values}")
