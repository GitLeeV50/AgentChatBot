# Global exception handlers

import functools
from typing import Any, Callable, Dict, Optional
from infrastructure.logging.manager import error_logger

class AgentBotError(Exception):
    """所有自定义异常的基类"""
    def __init__(self, message: str, code: int = 500, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.context = context or {}
        # 异常被抛出时自动记录到 errors.log
        error_logger.error(f"[{self.__class__.__name__}] Code: {self.code} | Message: {self.message} | Context: {self.context}")

class ConfigError(AgentBotError):
    """配置相关异常"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, code=400, context=context)

class LLMServiceError(AgentBotError):
    """LLM 服务调用异常"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, code=502, context=context)

class RAGError(AgentBotError):
    """RAG 检索或处理异常"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, code=503, context=context)

class ToolExecutionError(AgentBotError):
    """工具执行异常"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, code=500, context=context)

class FileIOError(AgentBotError):
    """文件读写相关异常"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, code=404, context=context)



def handle_exceptions(func: Callable) -> Callable:
    """全局异常处理装饰器 (顶层)"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except AgentBotError as e:
            # 由于 AgentBotError 已经在 __init__ 中 log 过，这里只需处理响应，不再重复记录 error
            # 可以在这里记录一条 INFO 级别的响应概览
            from infrastructure.logging.manager import logger
            logger.info(f"Caught handled exception: {e.message}")
            return {"status": "error", "code": e.code, "msg": e.message}
        except Exception as e:
            # 记录未预料的系统异常 (Panic)
            error_logger.critical(f"System Panic: {str(e)}", exc_info=True)
            return {"status": "error", "code": 500, "msg": "Internal Server Error"}
    return wrapper
