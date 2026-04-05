# LLM provider support
import os
from typing import Any, Dict, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.embeddings import DashScopeEmbeddings
from infrastructure.exceptions.handler import LLMServiceError
from infrastructure.logging.manager import logger
from dotenv import load_dotenv

# 加载 .env 环境变量
load_dotenv()

class LLMProvider:
    """
    LLM 提供商工厂：负责实例化具体的模型对象
    """
    
    @staticmethod
    def get_chat_model(provider: str, model_name: str, temperature: float = 0.7, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs) -> Any:
        """
        获取对话模型实例
        """
        provider = provider.lower()
        
        # 确定 API Key 优先级：传入参数 > 环境变量
        if not api_key:
            if provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
            elif provider in ["qwen", "dashscope"]:
                api_key = os.getenv("DASHSCOPE_API_KEY")
            elif provider in ["ollama", "lmstudio"]:
                api_key = "not-needed" # 本地模型通常不需要 key
        
        try:
            # 统一使用 ChatOpenAI 接口（Ollama 和 LMStudio 均支持 OpenAI 兼容接口）
            if provider in ["openai", "qwen", "dashscope", "ollama", "lmstudio"]:
                
                # 设置默认 base_url
                if not base_url:
                    if provider == "qwen":
                        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
                    elif provider == "ollama":
                        base_url = "http://localhost:11434/v1"
                    elif provider == "lmstudio":
                        base_url = "http://localhost:1234/v1"
                
                return ChatOpenAI(
                    model=model_name,
                    temperature=temperature,
                    api_key=api_key,
                    base_url=base_url if base_url else None,
                    **kwargs
                )
            
            else:
                raise LLMServiceError(f"不支持的 LLM 提供商: {provider}")
                
        except Exception as e:
            if isinstance(e, LLMServiceError):
                raise e
            raise LLMServiceError(f"实例化对话模型失败 ({provider}/{model_name}): {str(e)}")

    @staticmethod
    def get_embedding_model(provider: str, model_name: str, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs) -> Any:
        """
        获取向量嵌入模型实例
        """
        provider = provider.lower()
        
        if not api_key:
            if provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
            elif provider in ["qwen", "dashscope"]:
                api_key = os.getenv("DASHSCOPE_API_KEY")
            elif provider in ["ollama", "lmstudio"]:
                api_key = "not-needed"

        try:
            if provider == "qwen":
                # Tongyi Qianwen 使用专用嵌入类
                return DashScopeEmbeddings(
                    model=model_name,
                    dashscope_api_key=api_key,
                    **kwargs
                )
            elif provider in ["openai", "dashscope", "ollama", "lmstudio"]:
                
                if not base_url:
                    if provider == "dashscope":
                        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
                    elif provider == "ollama":
                        base_url = "http://localhost:11434/v1"
                    elif provider == "lmstudio":
                        base_url = "http://localhost:1234/v1"

                return OpenAIEmbeddings(
                    model=model_name,
                    api_key=api_key,
                    base_url=base_url if base_url else None,
                    **kwargs
                )
                
            else:
                raise LLMServiceError(f"不支持的 Embedding 提供商: {provider}")
                
        except Exception as e:
            if isinstance(e, LLMServiceError):
                raise e
            raise LLMServiceError(f"实例化 Embedding 模型失败 ({provider}/{model_name}): {str(e)}")
