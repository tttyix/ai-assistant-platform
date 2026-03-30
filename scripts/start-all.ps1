# 🚀 AI 助手集成平台 - 一键启动脚本 (E 盘版)

Write-Host "🚀 AI 助手集成平台 - 启动中..." -ForegroundColor Cyan
Write-Host "📍 项目位置：E:\ai-assistant-platform" -ForegroundColor Yellow
Write-Host "📚 知识库：C:\Users\tttyi\knowledge-base\" -ForegroundColor Yellow

# 1. 检查 Docker
Write-Host "`n📦 检查 Docker..." -ForegroundColor Yellow
$dockerStatus = Get-Service -Name "com.docker.service" -ErrorAction SilentlyContinue
if (-not $dockerStatus -or $dockerStatus.Status -ne "Running") {
    Write-Host "❌ Docker 未运行！" -ForegroundColor Red
    Write-Host "`n💡 请启动 Docker Desktop：" -ForegroundColor Yellow
    Write-Host "   1. 按 Win 键" -ForegroundColor White
    Write-Host "   2. 搜索 'Docker Desktop'" -ForegroundColor White
    Write-Host "   3. 点击启动" -ForegroundColor White
    Write-Host "   4. 等待图标变绿（约 30-60 秒）" -ForegroundColor White
    Write-Host "`n启动 Docker Desktop 后，重新运行此脚本！" -ForegroundColor Cyan
    exit 1
}
Write-Host "✅ Docker 运行正常" -ForegroundColor Green

# 2. 检查数据目录
Write-Host "`n📁 检查数据目录..." -ForegroundColor Yellow
$dataDirs = @(
    "E:/ai-assistant-platform/data/postgres",
    "E:/ai-assistant-platform/data/redis",
    "E:/ai-assistant-platform/data/qdrant",
    "E:/ai-assistant-platform/data/minio",
    "E:/ai-assistant-platform/data/logs"
)

foreach ($dir in $dataDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✅ 创建：$dir" -ForegroundColor Green
    } else {
        Write-Host "  ✅ 存在：$dir" -ForegroundColor Green
    }
}

# 3. 检查知识库
Write-Host "`n📚 检查知识库..." -ForegroundColor Yellow
$kbPath = "C:/Users/tttyi/knowledge-base"
if (Test-Path $kbPath) {
    $fileCount = (Get-ChildItem -Path $kbPath -Recurse -File -Filter "*.md").Count
    Write-Host "  ✅ 知识库存在：$kbPath" -ForegroundColor Green
    Write-Host "  📄 Markdown 文件数：$fileCount" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  知识库路径不存在" -ForegroundColor Yellow
}

# 4. 启动 Docker 容器
Write-Host "`n🐳 启动 Docker 容器..." -ForegroundColor Yellow
Set-Location "E:\ai-assistant-platform"
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker 容器启动成功" -ForegroundColor Green
} else {
    Write-Host "❌ Docker 容器启动失败" -ForegroundColor Red
    Write-Host "💡 查看日志：docker-compose logs" -ForegroundColor Yellow
    exit 1
}

# 5. 等待服务就绪
Write-Host "`n⏳ 等待服务就绪 (15 秒)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# 6. 验证服务
Write-Host "`n🔍 验证服务..." -ForegroundColor Yellow

$services = @{
    "PostgreSQL" = { docker exec ai-platform-postgres pg_isready -U ai_platform 2>&1 | Select-String "accepting connections" }
    "Redis" = { docker exec ai-platform-redis redis-cli -a ai_platform_redis_2026 ping 2>&1 | Select-String "PONG" }
    "Qdrant" = { try { Invoke-WebRequest -Uri "http://localhost:6333/" -TimeoutSec 5 -UseBasicParsing | Select-Object StatusCode } catch {} }
    "MinIO" = { try { Invoke-WebRequest -Uri "http://localhost:9000/minio/health/live" -TimeoutSec 5 -UseBasicParsing | Select-Object StatusCode } catch {} }
}

$allHealthy = $true

foreach ($service in $services.Keys) {
    try {
        $result = & $services[$service]
        if ($result) {
            Write-Host "  ✅ $service 正常" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  $service 未就绪" -ForegroundColor Yellow
            $allHealthy = $false
        }
    } catch {
        Write-Host "  ❌ $service 异常：$($_.Exception.Message)" -ForegroundColor Red
        $allHealthy = $false
    }
}

# 7. 显示访问信息
Write-Host "`n🎉 服务启动完成！" -ForegroundColor Green

if ($allHealthy) {
    Write-Host "`n📊 服务访问信息：" -ForegroundColor Cyan
    Write-Host "  ┌─────────────────────────────────────────────┐" -ForegroundColor DarkGray
    Write-Host "  │  PostgreSQL:  localhost:5432               │" -ForegroundColor White
    Write-Host "  │  Redis:       localhost:6379               │" -ForegroundColor White
    Write-Host "  │  Qdrant:      http://localhost:6333        │" -ForegroundColor White
    Write-Host "  │  MinIO:       http://localhost:9000        │" -ForegroundColor White
    Write-Host "  │  Console:     http://localhost:9001        │" -ForegroundColor White
    Write-Host "  └─────────────────────────────────────────────┘" -ForegroundColor DarkGray
    
    Write-Host "`n🔐 登录信息：" -ForegroundColor Cyan
    Write-Host "  ┌─────────────────────────────────────────────┐" -ForegroundColor DarkGray
    Write-Host "  │  PostgreSQL: ai_platform / ***secret_2026  │" -ForegroundColor White
    Write-Host "  │  Redis:      密码 / ***secret_2026         │" -ForegroundColor White
    Write-Host "  │  MinIO:      ai_platform_minio / ***       │" -ForegroundColor White
    Write-Host "  └─────────────────────────────────────────────┘" -ForegroundColor DarkGray
    
    Write-Host "`n📚 下一步：" -ForegroundColor Cyan
    Write-Host "  1. 激活 Python 虚拟环境" -ForegroundColor White
    Write-Host "  2. 安装依赖：pip install -r backend/requirements.txt" -ForegroundColor White
    Write-Host "  3. 构建知识库索引：python backend/src/knowledge/integrator.py" -ForegroundColor White
    Write-Host "  4. 启动后端服务：uvicorn backend.src.main:app --reload" -ForegroundColor White
} else {
    Write-Host "`n⚠️  部分服务未就绪，请检查日志：" -ForegroundColor Yellow
    Write-Host "  docker-compose logs" -ForegroundColor White
}

Write-Host "`n✅ 脚本执行完成！" -ForegroundColor Green
