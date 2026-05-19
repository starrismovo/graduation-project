# ==========================================
# AI 人岗匹配系统 - 后端启动脚本
# ==========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  🚀 启动后端服务" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 设置环境变量
Write-Host "📝 设置环境变量..." -ForegroundColor Yellow
if (-not $Env:ROAD2ALL_API_BASE) {
    $Env:ROAD2ALL_API_BASE = 'https://api.deepseek.com'
}
if (-not $Env:ROAD2ALL_MODEL) {
    $Env:ROAD2ALL_MODEL = 'deepseek-v4-pro'
}

# 激活虚拟环境
Write-Host "🔧 激活虚拟环境..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# 启动服务
Write-Host ""
Write-Host "✨ 启动 Uvicorn 服务器..." -ForegroundColor Cyan
Write-Host "   后端地址: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "   API 文档: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host ""

uvicorn main:app --reload --reload-exclude ".ocr_cache/*" --host 127.0.0.1 --port 8000
