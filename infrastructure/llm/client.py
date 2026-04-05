# Unified LLM client
from typing import Any, Optional
from infrastructure.llm.providers import LLMProvider
from infrastructure.config.manager import conf_loader
from infrastructure.logging.manager import logger
from infrastructure.exceptions.handler import ConfigError

class LLMClient:
    """
    统一 LLM 客户端：基于配置管理模型实例
    """
    
    def __init__(self):
        if conf_loader is None:
            raise ConfigError("配置未成功加载，无法初始化 LLM 客户端")
            
        self.llm_config = conf_loader.get("llm", {})
        
        # 1. 对话模型配置
        self.chat_provider = self.llm_config.get("chat_provider", "ollama")
        self.chat_model_name = self.llm_config.get("chat_model", "qwen3-4b")
        self.chat_api_key = self.llm_config.get("chat_api_key")
        self.chat_base_url = self.llm_config.get("chat_base_url")
        
        # 2. Embedding 模型配置
        self.embedding_provider = self.llm_config.get("embedding_provider", "openai")
        self.embedding_model_name = self.llm_config.get("embedding_model", "text-embedding-3-small")
        self.embedding_api_key = self.llm_config.get("embedding_api_key")
        self.embedding_base_url = self.llm_config.get("embedding_base_url")
        
        logger.info(f"LLM 客户端初始化: Chat[{self.chat_provider}/{self.chat_model_name}], Embedding[{self.embedding_provider}/{self.embedding_model_name}]")

    def get_chat_model(self, model_name: Optional[str] = None, temperature: Optional[float] = None, **kwargs) -> Any:
        """
        获取对话模型
        """
        temp = temperature if temperature is not None else self.llm_config.get("temperature", 0.7)
        model = model_name if model_name is not None else self.chat_model_name
        
        # 简单判断 provider
        provider = self.chat_provider
        if model.startswith("gpt"):
            provider = "openai"
            
        return LLMProvider.get_chat_model(
            provider=provider,
            model_name=model,
            temperature=temp,
            api_key=self.chat_api_key,
            base_url=self.chat_base_url,
            **kwargs
        )

    def get_embedding_model(self, **kwargs) -> Any:
        """
        获取 Embedding 模型
        """
        return LLMProvider.get_embedding_model(
            provider=self.embedding_provider,
            model_name=self.embedding_model_name,
            api_key=self.embedding_api_key,
            base_url=self.embedding_base_url,
            **kwargs
        )

# 单例模式，方便全局调用
_client = None

def get_llm_client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
