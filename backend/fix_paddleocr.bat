@REM PaddleOCR 快速修复脚本 (Windows)
@REM 直接运行这个文件，无需手动输入命令

@echo off
chcp 65001 > nul
cls

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║      🔧 PaddleOCR 兼容性问题 - 5分钟快速修复工具          ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM 检查是否在正确的目录
if not exist "venv\Scripts\activate.bat" (
    echo ❌ 错误: 找不到 venv\Scripts\activate.bat
    echo 请确保当前目录是: D:\Desktop\graduation-project\backend
    pause
    exit /b 1
)

echo 📝 第一步: 激活虚拟环境
call venv\Scripts\activate.bat

if %ERRORLEVEL% NEQ 0 (
    echo ❌ 虚拟环境激活失败
    pause
    exit /b 1
)

echo ✅ 虚拟环境已激活

echo.
echo 📝 第二步: 卸载旧版本 (可能需要 1-2 分钟)
pip uninstall paddleocr paddlepaddle -y

echo.
echo 📝 第三步: 安装兼容版本 (可能需要 3-5 分钟)
pip install paddleocr==2.7.0.3

if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  paddleocr 2.7.0.3 安装失败，尝试旧版本
    pip install paddleocr==2.6.0.3
)

pip install paddlepaddle==2.5.0

if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  paddlepaddle 2.5.0 安装失败，尝试旧版本
    pip install paddlepaddle==2.4.2
)

echo.
echo 📝 第四步: 验证安装
pip list | findstr paddle

echo.
echo ✅ 修复完成！

echo.
echo 📝 第五步: 重启后端服务
echo 现在你可以:
echo   1. 关闭这个窗口
echo   2. 重新启动后端: python main.py
echo   3. 检查日志中是否看到 "✅ PaddleOCR 初始化成功"

echo.
pause
