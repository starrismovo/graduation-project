@echo off
REM 以管理员权限启动 MySQL 服务
chcp 65001 >nul

echo [STEP 3] 正在启动 MySQL 服务...
net start MySQL57

if %errorLevel% equ 0 (
    echo [OK] MySQL 服务已启动
    timeout /t 3 /nobreak
) else (
    echo [ERROR] 无法启动 MySQL 服务 (错误码: %errorLevel%)
    echo.
    echo 可能的原因:
    echo - my.ini 配置有问题
    echo - D:\MySQLData 权限问题
    echo - MySQL 端口被占用
    echo.
    pause
    exit /b 1
)

echo.
echo [STEP 4] 验证 MySQL 状态...
timeout /t 2 /nobreak

for /f "tokens=3" %%a in ('sc query MySQL57 ^| find "STATE"') do (
    if "%%a"=="RUNNING" (
        echo [OK] MySQL 服务状态: RUNNING
    ) else (
        echo [WARNING] MySQL 服务状态: %%a
    )
)

echo.
echo ================================================================
echo ✓ 迁移完成！
echo ================================================================
echo.
echo 验证 Python 连接:
echo   python check_disk.py
echo.
echo 继续导入数据:
echo   python 招聘数据/import_zhilian.py 2
echo.
pause
