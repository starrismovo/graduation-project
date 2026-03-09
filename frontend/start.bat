@echo off
chcp 65001 >nul
cls

echo ========================================
echo   🚀 启动前端服务
echo ========================================
echo.

cd /d "%~dp0"

echo 📝 启动前端开发服务器...
echo   前端地址: http://localhost:5176
echo.

npm run dev

pause
