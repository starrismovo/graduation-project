@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ================================================================
echo MySQL 数据迁移 - 完成迁移步骤
echo ================================================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] 此脚本需要管理员权限!
    echo.
    echo 请按照以下方式运行:
    echo 1. 右键点击此文件
    echo 2. 选择 "以管理员身份运行"
    echo.
    pause
    exit /b 1
)

echo [OK] 已获得管理员权限
echo.

REM 步骤1: 停止MySQL
echo [STEP 1] 正在停止 MySQL 服务...
net stop MySQL57
if %errorLevel% equ 0 (
    echo [OK] MySQL 服务已停止
) else (
    echo [WARNING] 无法停止服务（可能未运行）
)
timeout /t 2 /nobreak

echo.
echo [STEP 2] 正在复制数据...
echo 源: C:\ProgramData\MySQL\MySQL Server 5.7\Data
echo 目标: D:\MySQLData
echo 这可能需要几分钟...
echo.

REM 步骤2: 复制数据
xcopy "C:\ProgramData\MySQL\MySQL Server 5.7\Data" "D:\MySQLData" /E /I /Y /Q
if %errorLevel% equ 0 (
    echo [OK] 数据复制完成
) else (
    echo [ERROR] 数据复制失败 (错误码: %errorLevel%)
    echo.
    echo 请检查:
    echo - D:\MySQLData 目录权限
    echo - D 盘空间是否足够
    echo.
    pause
    exit /b 1
)

echo.
echo [STEP 3] 正在启动 MySQL 服务...
net start MySQL57
if %errorLevel% equ 0 (
    echo [OK] MySQL 服务已启动
) else (
    echo [ERROR] 无法启动 MySQL 服务
    echo 错误码: %errorLevel%
    echo.
    echo 可能的原因:
    echo - my.ini 配置有问题
    echo - D:\MySQLData 权限问题
    echo.
    echo 恢复方法:
    echo 1. 运行: restore_mysql_config.bat
    echo 2. 检查事件查看器中 MySQL 的错误日志
    echo.
    pause
    exit /b 1
)

REM 步骤3: 验证
echo.
echo [STEP 4] 验证迁移...
timeout /t 3 /nobreak

echo.
echo ================================================================
echo ✓ 迁移完成!
echo ================================================================
echo.
echo 后续步骤:
echo 1. 运行 Python 进行验证:
echo    python check_disk.py
echo.
echo 2. 继续导入数据:
echo    python 招聘数据/import_zhilian.py 2
echo.
echo ================================================================
echo.
pause
