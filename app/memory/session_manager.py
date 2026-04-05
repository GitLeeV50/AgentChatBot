# Session memory management
from typing import List, Dict, Any, Optional
from infrastructure.logging.manager import logger

class SessionManager:
    """
    会话记忆管理器：基于内存存储短期对话历史
    """
    def __init__(self, max_messages: int = 10):
        # 存储结构: {session_id: [message_dict, ...]}
        self._sessions: Dict[str, List[Dict[str, str]]] = {}
        self.max_messages = max_messages

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """获取指定会话的历史记录"""
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        return self._sessions[session_id]

    def save_message(self, session_id: str, role: str, content: str):
        """保存单条消息到历史记录"""
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        
        # 追加消息
        self._sessions[session_id].append({"role": role, "content": content})
        
        # 滑动窗口裁剪：保持最近的 N 条消息
        if len(self._sessions[session_id]) > self.max_messages:
            self._sessions[session_id] = self._sessions[session_id][-self.max_messages:]
            logger.debug(f"会话 {session_id} 消息已达到上限，已执行滑动窗口裁剪")

    def get_history_str(self, session_id: str) -> str:
        """获取格式化后的历史记录字符串，用于注入 Prompt"""
        history = self.get_history(session_id)
        if not history:
            return ""
        
        formatted_history = []
        for msg in history:
            if msg["role"] == "user":
                role_label = "User"
            elif msg["role"] == "system":
                role_label = "System"
            else:
                role_label = "Assistant"
            formatted_history.append(f"{role_label}: {msg['content']}")
        
        return "\n".join(formatted_history)

    def clear_session(self, session_id: str):
        """清除指定会话的记忆"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"会话 {session_id} 的记忆已清除")

# 单例模式
_session_manager = None

def get_session_manager() -> SessionManager:
    global _session_manager
    if _session_manager is None:
        # 可以考虑从配置读取 max_messages
        from infrastructure.config.manager import conf_loader
        max_msgs = 10
        if conf_loader:
            max_msgs = conf_loader.get("llm", {}).get("max_history_messages", 10)
        _session_manager = SessionManager(max_messages=max_msgs)
    return _session_manager
