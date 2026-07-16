@echo off
cd /d "%~dp0"
if not exist venv\Scripts\python.exe (
    echo 未找到虚拟环境，正在创建...
    python -m venv venv
    venv\Scripts\pip install -r requirements.txt
)
venv\Scripts\python main.py
pause
