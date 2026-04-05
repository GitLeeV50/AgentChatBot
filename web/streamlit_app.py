# Streamlit main application logic
import streamlit as st
import uuid
from web.components import render_header, render_sidebar, render_chat_message, render_file_uploader
from app.agent.factory import AgentFactory
from app.memory.session_manager import get_session_manager
from infrastructure.logging.manager import logger

def main():
    # 1. 基础配置与头部渲染
    render_header()
    
    # 2. 初始化会话状态
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "messages" not in st.session_state:
        # 获取历史记录
        sm = get_session_manager()
        st.session_state.messages = sm.get_history(st.session_state.session_id)

    # 3. 渲染侧边栏
    config = render_sidebar()
    render_file_uploader()
    
    # 4. 渲染历史消息
    # 直接遍历渲染，Streamlit 的聊天组件会自动处理新消息的追加，不需要复杂的 _streaming 标记逻辑
    for message in st.session_state.messages:
        render_chat_message(message["role"], message["content"])

    # 5. 聊天输入
    prompt = st.chat_input("有什么我可以帮您的？")
    if prompt:
        # 展示用户消息 (但不在此手动 append，让 Agent Core 保存)
        render_chat_message("user", prompt)
        
        with st.chat_message("assistant"):
            try:
                # 创建 Agent
                agent = AgentFactory.create_agent(
                    temperature=config["temperature"]
                )
                
                # 思考过程容器
                status = st.status("🤖 Agent 正在思考...", expanded=True)
                thought_placeholder = status.empty() # 在状态栏内创建一个占位符
                full_thought = ""
                
                # 最终回答容器
                output_placeholder = st.empty()
                final_output = ""
                
                # 开始流式运行
                response_iter = agent.run_stream(prompt, session_id=st.session_state.session_id)
                
                for step in response_iter:
                    # 处理思考过程：拼接并实时更新
                    if "thought" in step:
                        full_thought += step["thought"]
                        # 限制思考内容的长度以防止渲染失败
                        full_thought = full_thought[-2000:]
                        # 使用 markdown 渲染拼接后的完整思考内容，保持格式
                        thought_placeholder.markdown(full_thought)
                    
                    # 处理最终输出：拼接并实时更新
                    if "output" in step:
                        final_output += step["output"]
                        output_placeholder.markdown(final_output)
                    
                    # 处理错误
                    if "error" in step:
                        st.error(f"Agent 出错: {step['error']}")
                
                # 更新状态栏
                status.update(label="✅ 思考完成！", state="complete", expanded=False)
                
                # 注意：这里也不手动 append 到 st.session_state.messages
                # 因为 Agent.run_stream 已经存入了 SessionManager，
                # 而 st.session_state.messages 引用的是同一个列表。
                
            except Exception as e:
                logger.error(f"Agent 运行出错: {e}")
                st.error(f"处理请求时出错: {str(e)}")
        
        # 强制刷新一次页面，使 history 循环正确读取最新的 messages 并渲染
        st.rerun()

if __name__ == "__main__":
    main()
