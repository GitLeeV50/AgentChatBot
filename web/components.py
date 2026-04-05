# Streamlit components
import streamlit as st
import os
from typing import List, Dict
from infrastructure.config.manager import conf_loader

def render_header():
    """渲染页面头部"""
    st.set_page_config(page_title="AgentBot - 智能助手", page_icon="🤖", layout="wide")
    st.title("ChatBot")
    st.markdown("---")

def render_sidebar():
    """渲染侧边栏配置"""
    with st.sidebar:
        st.header("系统配置")
        
        # 参数调整
        temperature = st.slider("Temperature (创造力)", 0.0, 1.0, 0.7, 0.1)
        
        st.markdown("---")
        st.header("                               知识库管理")
        
        # 显示当前知识库状态
        data_path = conf_loader.get("rag", {}).get("data_path", "data/external")
        st.info(f"当前数据目录: `{data_path}`")
        
        # 显示目录下的文件
        if os.path.exists(data_path):
            files = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f))]
            if files:
                st.subheader("当前知识库文件:")
                for file in files:
                    st.write(f"- {file}")
            else:
                st.write("目录为空")
        else:
            st.error(f"数据目录不存在: {data_path}")

        if st.button("刷新知识库", help="重新扫描目录并更新向量库"):
            with st.spinner("正在更新知识库..."):
                try:
                    from app.rag.service import RAGService
                    rag_service = RAGService()
                    rag_service.update_knowledge_base()
                    st.success("知识库更新成功！")
                except Exception as e:
                    st.error(f"更新失败: {e}")

        st.markdown("---")
        if st.button("清空当前对话", type="primary"):
            st.session_state.messages = []
            from app.memory.session_manager import get_session_manager
            get_session_manager().clear_session(st.session_state.session_id)
            st.rerun()

    return {"temperature": temperature}

def render_chat_message(role: str, content: str):
    """渲染单条聊天消息"""
    with st.chat_message(role):
        st.markdown(content)

def render_file_uploader():
    """渲染文件上传组件"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("上传新文档")
    uploaded_files = st.sidebar.file_uploader(
        "上传 PDF/MD/TXT 文件到知识库",
        type=["pdf", "md", "txt"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.sidebar.button("开始处理文件"):
            save_dir = conf_loader.get("rag", {}).get("data_path", "data/external")
            os.makedirs(save_dir, exist_ok=True)
            
            with st.spinner("正在保存并处理文件..."):
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(save_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                # 触发 RAG 更新
                from app.rag.service import RAGService
                RAGService().update_knowledge_base()
                st.sidebar.success(f"成功上传并处理 {len(uploaded_files)} 个文件！")
