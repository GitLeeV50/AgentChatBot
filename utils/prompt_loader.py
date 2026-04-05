# Prompt template loader
from infrastructure.logging.manager import logger
from infrastructure.config.manager import conf_loader
from utils.path_handler import get_abs_path
from infrastructure.exceptions.handler import ConfigError, FileIOError


def load_system_prompts():
    """加载 Agent 主提示词模板"""
    if not conf_loader:
        raise ConfigError("配置未成功加载，无法加载提示词")
        
    try:
        # 修正：从 prompts 层级读取
        relative_path = conf_loader.get("prompts", {}).get("main_prompt")
        if not relative_path:
            raise KeyError("main_prompt")
        system_prompt_path = get_abs_path(relative_path)
    except KeyError as e:
        raise ConfigError(f"YAML 配置项缺失: prompts.main_prompt", context={"key": str(e)})

    try:
        with open(system_prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        # 确保 system_prompt_path 在此处是可用的
        raise FileIOError(f"读取系统提示词文件失败: {str(e)}", context={"path": system_prompt_path})

def load_rag_prompts():
    """加载 RAG 总结提示词模板"""
    if not conf_loader:
        raise ConfigError("配置未成功加载，无法加载提示词")
        
    try:
        # 修正：从 prompts 层级读取
        relative_path = conf_loader.get("prompts", {}).get("rag_summarize")
        if not relative_path:
            raise KeyError("rag_summarize")
        rag_prompt_path = get_abs_path(relative_path)
    except KeyError as e:
        raise ConfigError(f"YAML 配置项缺失: prompts.rag_summarize", context={"key": str(e)})

    try:
        with open(rag_prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise FileIOError(f"读取 RAG 总结提示词文件失败: {str(e)}", context={"path": rag_prompt_path})

def load_role_prompts():
    """加载角色扮演提示词模板"""
    if not conf_loader:
        raise ConfigError("配置未成功加载，无法加载提示词")

    try:
        # 从 prompts 层级读取
        relative_path = conf_loader.get("prompts", {}).get("role_prompt")
        if not relative_path:
            raise KeyError("role_prompt")
        role_prompt_path = get_abs_path(relative_path)
    except KeyError as e:
        raise ConfigError(f"YAML 配置项缺失: prompts.role_prompt", context={"key": str(e)})

    try:
        with open(role_prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise FileIOError(f"读取角色扮演提示词文件失败: {str(e)}", context={"path": role_prompt_path})
