# 测试 Aira + CC 协作功能

Write-Host "🧪 测试 Aira + CC 协作功能" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor DarkGray

# 1. 检查服务状态
Write-Host "`n1️⃣ 检查服务状态..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ 后端服务运行正常" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ 后端服务未响应" -ForegroundColor Red
    Write-Host "   请确保服务已启动：cd E:\ai-assistant-platform\backend; ..\venv\Scripts\uvicorn src.main:app --reload"
    exit 1
}

# 2. 检查 API 文档
Write-Host "`n2️⃣ 检查 API 文档..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ API 文档可访问" -ForegroundColor Green
        Write-Host "   📍 地址：http://localhost:8000/docs" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ⚠️  API 文档访问失败" -ForegroundColor Yellow
}

# 3. 检查工作流路由
Write-Host "`n3️⃣ 检查工作流路由..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/openapi.json" -TimeoutSec 10 -UseBasicParsing
    $openapi = $response.Content | ConvertFrom-Json
    
    $workflowPaths = $openapi.paths.PSObject.Properties.Name | Where-Object { $_ -like "*workflow*" }
    
    if ($workflowPaths.Count -gt 0) {
        Write-Host "   ✅ 工作流路由已注册" -ForegroundColor Green
        foreach ($path in $workflowPaths) {
            Write-Host "      - $path" -ForegroundColor Gray
        }
    } else {
        Write-Host "   ⚠️  工作流路由未注册" -ForegroundColor Yellow
        Write-Host "   可能需要重启服务" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ⚠️  无法获取 OpenAPI 规范" -ForegroundColor Yellow
}

# 4. 显示使用说明
Write-Host "`n📋 使用说明" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor DarkGray
Write-Host ""
Write-Host "1. 访问 API 文档测试：" -ForegroundColor White
Write-Host "   http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. 使用 curl 测试：" -ForegroundColor White
Write-Host @"
curl -X POST "http://localhost:8000/api/v1/workflows/execute" `
  -H "Content-Type: application/json" `
  -d '{
    "task": "帮我创建一个简单的 Python 计算器",
    "mode": "aira+cc"
  }'
"@
Write-Host ""
Write-Host "3. 查看任务历史：" -ForegroundColor White
Write-Host "   curl http://localhost:8000/api/v1/workflows/history" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. 查看使用指南：" -ForegroundColor White
Write-Host "   E:\ai-assistant-platform\docs\WORKFLOW-GUIDE.md" -ForegroundColor Cyan

Write-Host "`n✅ 测试完成！" -ForegroundColor Green
Write-Host ""
