@echo off
chcp 65001 >nul
cls

echo ========================================
echo   🚀 启动后端服务
echo ========================================
echo.

cd /d "%~dp0"

echo 📝 设置环境变量...
if "%ROAD2ALL_API_BASE%"=="" set ROAD2ALL_API_BASE=https://api.deepseek.com
if "%ROAD2ALL_MODEL%"=="" set ROAD2ALL_MODEL=deepseek-v4-pro

echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo ✨ 启动 Uvicorn 服务器...
echo   后端地址: http://127.0.0.1:8000
echo   API 文档: http://127.0.0.1:8000/docs
echo.

python -m uvicorn main:app --reload --reload-exclude ".ocr_cache/*" --host 127.0.0.1 --port 8000

pause
