#!/usr/bin/env powershell
# 前端环境验证脚本

Write-Host "🔍 前端集成检查清单`n" -ForegroundColor Blue

# 检查 Node.js
Write-Host "检查 Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>$null
if ($nodeVersion) {
    Write-Host "✅ Node.js 版本: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Node.js 未安装或不在 PATH 中" -ForegroundColor Red
    exit 1
}

# 检查 npm
Write-Host "检查 npm..." -ForegroundColor Yellow
$npmVersion = npm --version 2>$null
if ($npmVersion) {
    Write-Host "✅ npm 版本: $npmVersion" -ForegroundColor Green
} else {
    Write-Host "❌ npm 未安装或不在 PATH 中" -ForegroundColor Red
    exit 1
}

# 检查 package.json
Write-Host "检查 package.json..." -ForegroundColor Yellow
if (Test-Path "frontend/package.json") {
    Write-Host "✅ package.json 存在" -ForegroundColor Green
} else {
    Write-Host "❌ package.json 未找到" -ForegroundColor Red
    exit 1
}

# 检查 src 目录结构
Write-Host "`n📂 检查前端源代码结构...`n" -ForegroundColor Yellow
$requiredFiles = @(
    "frontend/src/main.ts",
    "frontend/src/App.vue",
    "frontend/src/views/HomeView.vue",
    "frontend/src/views/IndexView.vue",
    "frontend/src/utils/request.ts",
    "frontend/src/stores/user.ts",
    "frontend/src/router/index.ts",
    "frontend/src/types/assessment.ts"
)

$allExists = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file 未找到" -ForegroundColor Red
        $allExists = $false
    }
}

# 检查关键组件
Write-Host "`n🧩 检查组件文件...`n" -ForegroundColor Yellow
$components = @(
    "frontend/src/components/RadarChart.vue",
    "frontend/src/components/EmptyState.vue",
    "frontend/src/components/AssessmentHistory.vue",
    "frontend/src/components/JobCard.vue"
)

foreach ($component in $components) {
    if (Test-Path $component) {
        Write-Host "✅ $component" -ForegroundColor Green
    } else {
        Write-Host "❌ $component 未找到" -ForegroundColor Red
    }
}

# 检查后端连接性
Write-Host "`n🔌 检查后端连接...`n" -ForegroundColor Yellow
$backendUrl = "http://localhost:8000"
try {
    $response = Invoke-WebRequest -Uri $backendUrl -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 后端服务正在运行于 $backendUrl" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  后端服务未响应 (这是正常的，如果还未启动)" -ForegroundColor Yellow
    Write-Host "   启动后端: cd backend && python -m uvicorn main:app --reload" -ForegroundColor Yellow
}

Write-Host "`n✨ 前端检查完成！`n" -ForegroundColor Green
Write-Host "下一步操作:`n" -ForegroundColor Cyan
Write-Host "1. 在 frontend 目录运行: npm install" -ForegroundColor Cyan
Write-Host "2. 运行: npm run dev" -ForegroundColor Cyan
Write-Host "3. 访问: http://localhost:5173" -ForegroundColor Cyan
