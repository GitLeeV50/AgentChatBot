# Interface for the AgentBot

from infrastructure.exceptions.handler import handle_exceptions
from utils.file_handler import get_file_md5_hex

@handle_exceptions
def ask_agent(query: str, session_id: str = "default"):
    """
    Agent 对外统一接口 (顶层)
    """
    # 示例：调用底层工具，底层会抛出 FileIOError
    # md5 = get_file_md5_hex("non_existent_file.txt") 
    
    # 模拟业务逻辑
    if not query:
        from infrastructure.exceptions.handler import AgentBotError
        raise AgentBotError("Query cannot be empty", code=400)
        
    return {
        "status": "success",
        "data": f"Echo: {query} for session {session_id}"
    }

if __name__ == "__main__":
    # 测试正常调用
    print(ask_agent("Hello"))
    
    # 测试业务异常
    print(ask_agent(""))
    
    # 测试底层工具抛出的异常
    @handle_exceptions
    def test_file_error():
        return get_file_md5_hex("not_found.txt")
    
    print(test_file_error())
