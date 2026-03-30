@echo off
echo ================================================
echo    AI 助手集成平台 - 后端启动脚本
echo ================================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.12+
    exit /b 1
)
echo [1/4] Python 已就绪

REM 进入 backend 目录
cd /d "%~dp0backend"

REM 安装依赖
echo [2/4] 正在安装 Python 依赖...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [错误] 依赖安装失败
    exit /b 1
)
echo [3/4] 依赖安装完成

REM 初始化数据库
echo [4/4] 正在初始化数据库...
python -c "from src.database import init_db; init_db()"

echo.
echo ================================================
echo    正在启动 FastAPI 服务...
echo    API 文档：http://localhost:8000/docs
echo    健康检查：http://localhost:8000/health
echo ================================================
echo.

REM 启动服务
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
