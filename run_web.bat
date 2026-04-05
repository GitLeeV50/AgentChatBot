@echo off
REM run_web.bat - 一键启动 Streamlit Web 界面

echo 正在激活虚拟环境...
call .venv\Scripts\activate.bat

echo 正在检查端口 8502...

REM 查找占用8502端口的进程PID
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8502" ^| find "LISTENING"') do (
    set PID=%%a
)

REM 如果找到PID，则结束该进程
if defined PID (
    echo 发现占用端口 8502 的进程 PID: %PID%，正在结束...
    taskkill /F /PID %PID%
    echo 进程已结束
) else (
    echo 端口 8502 未被占用
)

REM 等待1秒确保端口释放
timeout /t 1 /nobreak >nul

echo 正在启动 Streamlit Web 界面...
python run_web.py

pause