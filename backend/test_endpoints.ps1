# Test script for Phase 1 endpoints

Write-Host "Testing Mini RAG API Endpoints" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "1. Testing GET /health" -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get
    Write-Host "✓ Health check passed" -ForegroundColor Green
    $health | ConvertTo-Json
} catch {
    Write-Host "✗ Health check failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Ingest Endpoint
Write-Host "2. Testing POST /ingest" -ForegroundColor Yellow
try {
    $ingestBody = @{
        text = "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of intelligent agents."
        title = "AI Introduction"
        source = "test_doc"
    } | ConvertTo-Json
    
    $ingestResult = Invoke-RestMethod -Uri "http://localhost:8001/ingest" -Method Post -Body $ingestBody -ContentType "application/json"
    Write-Host "✓ Ingest endpoint passed" -ForegroundColor Green
    $ingestResult | ConvertTo-Json
} catch {
    Write-Host "✗ Ingest endpoint failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: Query Endpoint
Write-Host "3. Testing POST /query" -ForegroundColor Yellow
try {
    $queryBody = @{
        query = "What is artificial intelligence?"
        top_k = 3
    } | ConvertTo-Json
    
    $queryResult = Invoke-RestMethod -Uri "http://localhost:8001/query" -Method Post -Body $queryBody -ContentType "application/json"
    Write-Host "✓ Query endpoint passed" -ForegroundColor Green
    $queryResult | ConvertTo-Json -Depth 5
} catch {
    Write-Host "✗ Query endpoint failed: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Phase 1 endpoint testing complete!" -ForegroundColor Cyan
