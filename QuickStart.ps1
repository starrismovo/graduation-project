#!/bin/env powershell
<#
.DESCRIPTION
一键启动脚本 - 启动前后端服务
Quick Startup Script - Start both Frontend and Backend
#>

# 项目根目录
$ProjectRoot = "d:\Desktop\graduation-project"

Write-Host @"
╔════════════════════════════════════════════════════════════╗
║        应聘流程 - 快速启动脚本                              ║
║        Job Application Flow - Quick Start Script           ║
╚════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# 检查是否在正确的目录
if (-not (Test-Path "$ProjectRoot\backend\main.py")) {
    Write-Host "❌ 后端文件不存在: $ProjectRoot\backend\main.py" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "$ProjectRoot\frontend\package.json")) {
    Write-Host "❌ 前端文件不存在: $ProjectRoot\frontend\package.json" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ 项目结构检查通过" -ForegroundColor Green

# ============================================================================
# 启动后端
# ============================================================================

Write-Host "`n📦 启动后端服务..." -ForegroundColor Yellow
Write-Host "   位置: $ProjectRoot\backend" -ForegroundColor Gray

$BackendDir = "$ProjectRoot\backend"
$BackendScript = "$BackendDir\main.py"

# 在新 PowerShell 窗口中启动后端
Write-Host "   ⏳ 在新窗口中启动后端..." -ForegroundColor Cyan

$BackendProcess = Start-Process -FilePath "powershell" `
    -ArgumentList "-NoExit", "-Command", "cd '$BackendDir'; python main.py" `
    -PassThru `
    -WindowStyle Normal

Write-Host "   ✅ 后端进程已启动 (PID: $($BackendProcess.Id))" -ForegroundColor Green
Write-Host "   📍 后端地址: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "   📚 API 文档: http://127.0.0.1:8000/docs" -ForegroundColor Cyan

# 等待后端启动
Write-Host "   ⏳ 等待后端启动 (20 秒)..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# 检查后端是否运行
$BackendReady = $false
for ($i = 0; $i -lt 20; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/docs" -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $BackendReady = $true
            Write-Host "   ✅ 后端服务已就绪！" -ForegroundColor Green
            break
        }
    } catch {
        # 继续等待
    }
    
    if ($i -lt 19) {
        Write-Host "   ⏳ 等待中... ($($i + 1)/20)" -ForegroundColor Gray
        Start-Sleep -Seconds 1
    }
}

if (-not $BackendReady) {
    Write-Host "   ⚠️  后端可能未完全启动，继续启动前端..." -ForegroundColor Yellow
}

# ============================================================================
# 启动前端
# ============================================================================

Write-Host "`n📱 启动前端服务..." -ForegroundColor Yellow
Write-Host "   位置: $ProjectRoot\frontend" -ForegroundColor Gray

$FrontendDir = "$ProjectRoot\frontend"

# 检查 node_modules
if (-not (Test-Path "$FrontendDir\node_modules")) {
    Write-Host "   🔧 node_modules 不存在，运行 npm install..." -ForegroundColor Yellow
    Push-Location $FrontendDir
    npm install
    Pop-Location
}

# 在新 PowerShell 窗口中启动前端
Write-Host "   ⏳ 在新窗口中启动前端..." -ForegroundColor Cyan

$FrontendProcess = Start-Process -FilePath "powershell" `
    -ArgumentList "-NoExit", "-Command", "cd '$FrontendDir'; npm run dev" `
    -PassThru `
    -WindowStyle Normal

Write-Host "   ✅ 前端进程已启动 (PID: $($FrontendProcess.Id))" -ForegroundColor Green
Write-Host "   📍 前端地址: http://localhost:5173" -ForegroundColor Cyan

# 等待前端启动
Write-Host "   ⏳ 等待前端启动 (15 秒)..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# ============================================================================
# 启动完成
# ============================================================================

Write-Host "`n" -ForegroundColor Gray
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                  ✅ 启动完成！                             ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host @"

📊 服务状态:
  ✅ 后端: http://127.0.0.1:8000
  ✅ 前端: http://localhost:5173
  ✅ API 文档: http://127.0.0.1:8000/docs

📋 快速测试:
  1. 打开浏览器，访问 http://localhost:5173
  2. 登录或注册候选人账户
  3. 上传简历并填写基本信息
  4. 进入岗位选择页面
  5. 选择一个岗位并点击"确认应聘"
  6. 应该看到成功提示 ✅
  
⚠️  注意:
  • 后端和前端分别在两个窗口运行
  • 关闭任何窗口将停止相应的服务
  • 要停止所有服务，关闭这两个窗口

🔍 调试:
  • 后端日志：在后端窗口查看
  • 前端日志：按 F12 打开开发者工具
  • API 文档：http://127.0.0.1:8000/docs

📖 更多帮助:
  • 启动指南: COMPLETE_STARTUP_GUIDE.md
  • 前端调试: FRONTEND_DEBUG_GUIDE.md
  • 修复详情: FIX_422_ERROR.md
  • API 验证: python verify_complete_flow.py

"@ -ForegroundColor Cyan

Write-Host "按 Enter 键关闭此窗口..." -ForegroundColor Yellow
Read-Host
