#!/usr/bin/env powershell
# AI 智能面试系统 - 前后端一体启动脚本
# 在项目根目录运行此脚本

Write-Host "🚀 AI 智能面试系统 - 前后端启动脚本`n" -ForegroundColor Cyan
Write-Host "这个脚本将帮您自动启动前后端服务`n" -ForegroundColor Yellow

# 记录启动时间
$startTime = Get-Date

# 检查后端环境
Write-Host "1️⃣  检查后端环境...`n" -ForegroundColor Blue
if (!(Test-Path "backend\main.py")) {
    Write-Host "❌ 找不到后端文件: backend\main.py" -ForegroundColor Red
    exit 1
}

if (!(Test-Path "backend\.env")) {
    Write-Host "⚠️  warning: 后端配置文件 backend\.env 不存在`n" -ForegroundColor Yellow
}

# 检查前端环境
Write-Host "2️⃣  检查前端环境...`n" -ForegroundColor Blue
if (!(Test-Path "frontend\package.json")) {
    Write-Host "❌ 找不到前端文件: frontend\package.json" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== 后端启动选项 ===`n" -ForegroundColor Cyan
Write-Host "1. 仅启动后端" -ForegroundColor Cyan
Write-Host "2. 启动后端和前端（推荐）" -ForegroundColor Cyan
Write-Host "3. 只显示说明，不启动" -ForegroundColor Cyan

$choice = Read-Host "`n请选择 (1-3)"

switch ($choice) {
    "1" {
        Write-Host "`n📍 仅启动后端服务...`n" -ForegroundColor Green
        Write-Host "后端启动步骤：`n" -ForegroundColor Yellow
        Write-Host "cd backend" -ForegroundColor Gray
        Write-Host "venv\Scripts\activate" -ForegroundColor Gray
        Write-Host "pip install -r requirements.txt  # 如果需要" -ForegroundColor Gray
        Write-Host "python init_assessment.py        # 初始化数据库（首次）" -ForegroundColor Gray
        Write-Host "python -m uvicorn main:app --reload"`n -ForegroundColor Gray
        
        Write-Host "💡 提示: 后端将在 http://localhost:8000 启动`n" -ForegroundColor Cyan
        
        # 执行后端启动
        Set-Location backend
        if (!(Test-Path "venv")) {
            Write-Host "虚拟环境不存在，创建中..." -ForegroundColor Yellow
            python -m venv venv
        }
        
        & venv\Scripts\activate.ps1
        Write-Host "安装后端依赖中..." -ForegroundColor Yellow
        pip install -q -r requirements.txt
        
        Write-Host "`n初始化数据库..." -ForegroundColor Yellow
        python init_assessment.py
        
        Write-Host "`n启动后端服务...`n" -ForegroundColor Green
        python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
        break
    }
    
    "2" {
        Write-Host "`n📍 启动后端和前端服务...`n" -ForegroundColor Green
        
        # 启动后端
        Write-Host "🔧 后端启动中..." -ForegroundColor Yellow
        $backendProcess = Start-Process powershell -ArgumentList @"
            `$ProgressPreference = 'SilentlyContinue'
            Set-Location "$PWD\backend"
            if (!(Test-Path "venv")) {
                python -m venv venv
            }
            & venv\Scripts\activate.ps1
            pip install -q -r requirements.txt
            Write-Host "初始化数据库..." -ForegroundColor Yellow
            python init_assessment.py
            Write-Host "启动后端服务..."
            python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
"@ -WindowStyle Normal -PassThru
        
        Write-Host "✅ 后端进程启动: PID $($backendProcess.Id)" -ForegroundColor Green
        
        # 等待后端启动
        Write-Host "`n等待后端启动 (30秒)..." -ForegroundColor Yellow
        for ($i = 0; $i -lt 30; $i++) {
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:8000" -ErrorAction SilentlyContinue
                if ($response.StatusCode -eq 200) {
                    Write-Host "✅ 后端已启动！`n" -ForegroundColor Green
                    break
                }
            } catch {
                # 继续等待
            }
            Start-Sleep -Seconds 1
            Write-Host -NoNewline "."
        }
        
        # 启动前端
        Write-Host "`n🎨 前端启动中..." -ForegroundColor Yellow
        $frontendProcess = Start-Process powershell -ArgumentList @"
            `$ProgressPreference = 'SilentlyContinue'
            Set-Location "$PWD\frontend"
            Write-Host "安装前端依赖..." -ForegroundColor Yellow
            npm install -q --legacy-peer-deps 2>$null
            Write-Host "启动前端开发服务..."
            npm run dev
"@ -WindowStyle Normal -PassThru
        
        Write-Host "✅ 前端进程启动: PID $($frontendProcess.Id)" -ForegroundColor Green
        
        # 等待前端启动
        Write-Host "`n等待前端启动 (20秒)..." -ForegroundColor Yellow
        for ($i = 0; $i -lt 20; $i++) {
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:5173" -ErrorAction SilentlyContinue
                if ($response.StatusCode -eq 200) {
                    Write-Host "✅ 前端已启动！`n" -ForegroundColor Green
                    break
                }
            } catch {
                # 继续等待
            }
            Start-Sleep -Seconds 1
            Write-Host -NoNewline "."
        }
        
        # 显示访问信息
        Write-Host "`n" -ForegroundColor Green
        Write-Host "════════════════════════════════════════" -ForegroundColor Green
        Write-Host "✨ 系统启动完成！" -ForegroundColor Green
        Write-Host "════════════════════════════════════════" -ForegroundColor Green
        Write-Host ""
        Write-Host "📍 访问地址：" -ForegroundColor Cyan
        Write-Host "  后端 API: http://localhost:8000" -ForegroundColor Gray
        Write-Host "  前端应用: http://localhost:5173" -ForegroundColor Gray
        Write-Host "  API 文档: http://localhost:8000/docs" -ForegroundColor Gray
        Write-Host ""
        Write-Host "📊 进程信息：" -ForegroundColor Cyan
        Write-Host "  后端进程 ID: $($backendProcess.Id)" -ForegroundColor Gray
        Write-Host "  前端进程 ID: $($frontendProcess.Id)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "🛑 关闭提示：" -ForegroundColor Cyan
        Write-Host "  关闭此窗口将同时关闭两个进程" -ForegroundColor Gray
        Write-Host ""
        
        # 保持两个进程运行
        Write-Host "保持进程运行中... (按 Ctrl+C 退出)`n" -ForegroundColor Yellow
        while ($true) {
            if (!$backendProcess.HasExited -and !$frontendProcess.HasExited) {
                Start-Sleep -Seconds 5
            } else {
                Write-Host "`n⚠️  某个进程已退出！" -ForegroundColor Yellow
                if ($backendProcess.HasExited) {
                    Write-Host "后端进程已退出" -ForegroundColor Red
                }
                if ($frontendProcess.HasExited) {
                    Write-Host "前端进程已退出" -ForegroundColor Red
                }
                break
            }
        }
        break
    }
    
    "3" {
        Write-Host "`n📖 手动启动步骤：`n" -ForegroundColor Cyan
        
        Write-Host "【后端启动】" -ForegroundColor Yellow
        Write-Host "  1. 打开新的 PowerShell 窗口" -ForegroundColor Gray
        Write-Host "  2. 进入后端目录：cd backend" -ForegroundColor Gray
        Write-Host "  3. 激活虚拟环境：venv\Scripts\activate" -ForegroundColor Gray
        Write-Host "  4. 初始化数据库（首次）：python init_assessment.py" -ForegroundColor Gray
        Write-Host "  5. 启动服务：python -m uvicorn main:app --reload" -ForegroundColor Gray
        Write-Host ""
        
        Write-Host "【前端启动】" -ForegroundColor Yellow
        Write-Host "  1. 打开新的 PowerShell 窗口" -ForegroundColor Gray
        Write-Host "  2. 进入前端目录：cd frontend" -ForegroundColor Gray
        Write-Host "  3. 安装依赖（首次）：npm install" -ForegroundColor Gray
        Write-Host "  4. 启动服务：npm run dev" -ForegroundColor Gray
        Write-Host ""
        
        Write-Host "【访问应用】" -ForegroundColor Yellow
        Write-Host "  后端 API 文档：http://localhost:8000/docs" -ForegroundColor Gray
        Write-Host "  前端应用：http://localhost:5173" -ForegroundColor Gray
        Write-Host ""
        
        Write-Host "【验证集成】" -ForegroundColor Yellow
        Write-Host "  cd backend && python test_assessment_api.py" -ForegroundColor Gray
        break
    }
    
    default {
        Write-Host "❌ 无效的选择" -ForegroundColor Red
        exit 1
    }
}

$endTime = Get-Date
$duration = $endTime - $startTime
Write-Host "`n⏱️  运行时间: $($duration.TotalSeconds) 秒" -ForegroundColor Green
