@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ================================================================
echo MySQL 配置还原 - 恢复到 C 盘配置
echo ================================================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] 此脚本需要管理员权限!
    echo 请以管理员身份运行
    pause
    exit /b 1
)

echo [WARNING] 这将恢复原来的MySQL配置（指向C盘）
echo.

REM 寻找最新的备份文件
set "CONFIG_DIR=C:\ProgramData\MySQL\MySQL Server 5.7"
set "BACKUP_FILE="

for /f "tokens=* delims=" %%A in ('dir "%CONFIG_DIR%\my.ini.backup_*" /B /O-D 2^>nul') do (
    set "BACKUP_FILE=%%A"
    goto :found
)

if not defined BACKUP_FILE (
    echo [ERROR] 找不到备份文件
    echo 备份文件应该在: %CONFIG_DIR%\my.ini.backup_*
    echo.
    pause
    exit /b 1
)

:found
echo [OK] 找到备份文件: !BACKUP_FILE!
echo.

REM 停止MySQL
echo [STEP 1] 正在停止 MySQL 服务...
net stop MySQL57
timeout /t 2 /nobreak

REM 恢复备份
echo [STEP 2] 正在恢复配置文件...
copy "%CONFIG_DIR%\!BACKUP_FILE!" "%CONFIG_DIR%\my.ini" /Y >nul
if %errorLevel% equ 0 (
    echo [OK] 配置已恢复
) else (
    echo [ERROR] 无法恢复配置
    pause
    exit /b 1
)

REM 启动MySQL
echo [STEP 3] 正在启动 MySQL 服务...
net start MySQL57
if %errorLevel% equ 0 (
    echo [OK] MySQL 服务已启动
) else (
    echo [ERROR] 无法启动 MySQL 服务
    pause
    exit /b 1
)

echo.
echo ================================================================
echo ✓ 配置已恢复
echo ================================================================
echo.
pause
