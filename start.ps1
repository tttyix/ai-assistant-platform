# AI 助手集成平台 - 一键启动脚本
# 功能：启动后端服务 + 打开简洁前端界面

Write-Host "🚀 AI 助手集成平台 - 启动中..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor DarkGray

# 1. 检查 Docker 服务
Write-Host "`n📦 检查 Docker 服务..." -ForegroundColor Yellow
try {
    $dockerStatus = docker-compose ps 2>&1
    if ($dockerStatus -match "Up") {
        Write-Host "   ✅ Docker 服务运行正常" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Docker 服务未运行，建议先执行：docker-compose up -d" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Docker 未安装或未启动" -ForegroundColor Red
}

# 2. 激活虚拟环境
Write-Host "`n🐍 激活 Python 虚拟环境..." -ForegroundColor Yellow
$venvPath = Join-Path $PSScriptRoot "venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host "   ✅ 虚拟环境已激活" -ForegroundColor Green
} else {
    Write-Host "   ❌ 虚拟环境不存在，请先创建：python -m venv venv" -ForegroundColor Red
    exit 1
}

# 3. 启动后端服务
Write-Host "`n🔧 启动后端服务..." -ForegroundColor Yellow
Write-Host "   后端地址：http://localhost:8000" -ForegroundColor Gray
Write-Host "   API 文档：http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "   健康检查：http://localhost:8000/health" -ForegroundColor Gray

# 使用 Start-Process 在后台启动 uvicorn
$uvicornPath = Join-Path $PSScriptRoot "venv\Scripts\uvicorn.exe"
if (Test-Path $uvicornPath) {
    Start-Process -FilePath $uvicornPath `
                  -ArgumentList "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" `
                  -WorkingDirectory (Join-Path $PSScriptRoot "src") `
                  -WindowStyle Normal
    
    Write-Host "   ✅ 后端服务已启动" -ForegroundColor Green
    Start-Sleep -Seconds 3  # 等待服务启动
} else {
    Write-Host "   ❌ uvicorn 未安装，请执行：pip install uvicorn" -ForegroundColor Red
    exit 1
}

# 4. 打开简洁前端界面
Write-Host "`n🎨 打开简洁前端界面..." -ForegroundColor Yellow
$simpleHtml = Join-Path $PSScriptRoot "..\simple.html"
if (Test-Path $simpleHtml) {
    Start-Process $simpleHtml
    Write-Host "   ✅ 前端界面已打开" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  找不到 simple.html，但不影响使用" -ForegroundColor Yellow
    Write-Host "      可以访问 http://localhost:8000/docs 使用 API 文档" -ForegroundColor Gray
}

# 5. 显示使用说明
Write-Host "`n📋 使用说明" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor DarkGray
Write-Host ""
Write-Host "1. 简洁界面已自动打开（如果找不到的话）：" -ForegroundColor White
Write-Host "   E:\ai-assistant-platform\simple.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. API 文档（Swagger UI）：" -ForegroundColor White
Write-Host "   http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. 健康检查：" -ForegroundColor White
Write-Host "   http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. 停止服务：" -ForegroundColor White
Write-Host "   关闭这个 PowerShell 窗口即可" -ForegroundColor Gray
Write-Host ""
Write-Host "🎉 启动完成！开始使用吧！" -ForegroundColor Green
Write-Host ""

# 保持窗口打开
Write-Host "按任意键退出..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
