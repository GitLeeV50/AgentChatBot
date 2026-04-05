@echo off
REM stop_web.bat - 停止 Streamlit 服务

echo 正在停止端口 8502 的服务...

for /f "tokens=5" %%a in ('netstat -aon ^| find ":8502" ^| find "LISTENING"') do (
    set PID=%%a
)

if defined PID (
    echo 正在终止进程 PID: %PID%
    taskkill /F /PID %PID%
    echo 服务已停止
) else (
    echo 未找到运行在端口 8502 的服务
)

pause