# Entry point for the Streamlit application
import os
import sys
import subprocess

def main():
    """启动 Streamlit 应用"""
    # 获取当前项目的根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 将项目根目录添加到 python 路径，确保可以正确导入模块
    sys.path.insert(0, project_root)
    
    # Streamlit 应用的文件路径
    app_path = os.path.join(project_root, "web", "streamlit_app.py")

    # 检查是否被 streamlit 直接调用，防止递归
    if any("streamlit" in arg for arg in sys.argv[0:2]):
        # 直接运行 streamlit_app.py
        import runpy
        runpy.run_path(app_path, run_name="__main__")
    else:
        # 构造运行命令
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            app_path,
            "--server.port=8502",
            "--server.address=0.0.0.0"
        ]
        print(f"Starting AgentBot Web Interface...")
        print(f"URL: http://localhost:8502")
        try:
            subprocess.run(cmd, check=True)
        except KeyboardInterrupt:
            print("\n[INFO] Stopped by user.")
        except Exception as e:
            print(f"[ERROR] Startup failed: {e}")

if __name__ == "__main__":
    main()
