# Synapse — Demo Setup Script (Windows)
# Seeds static skill graphs and validates environment.

$ErrorActionPreference = "Stop"

Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        SYNAPSE — Demo Environment Setup      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check required env vars
if (-not $env:GEMINI_API_KEY) {
    Write-Host "❌ GEMINI_API_KEY not set. Export it first:" -ForegroundColor Red
    Write-Host "   `$env:GEMINI_API_KEY='your-key-here'"
    exit 1
}

$PROJECT_ID = if ($env:PROJECT_ID) { $env:PROJECT_ID } else { "synapse-dev" }
$BUCKET = if ($env:SKILL_GRAPHS_BUCKET) { $env:SKILL_GRAPHS_BUCKET } else { "${PROJECT_ID}-skill-graphs" }

Write-Host "📋 Configuration:"
Write-Host "   PROJECT_ID: $PROJECT_ID"
Write-Host "   BUCKET:     $BUCKET"
Write-Host ""

# Step 1: Upload static skill graphs
Write-Host "📦 Step 1: Uploading static skill graphs..." -ForegroundColor Yellow
if (Get-Command gsutil -ErrorAction SilentlyContinue) {
    gsutil -m cp -r skill-graphs/product/* "gs://${BUCKET}/product/"
    gsutil -m cp -r skill-graphs/industries/* "gs://${BUCKET}/industries/"
    Write-Host "   ✅ Static graphs uploaded to GCS" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  gsutil not found — skipping GCS upload (graphs available locally)" -ForegroundColor Gray
}

# Step 2: Install Python dependencies
Write-Host "`n🐍 Step 2: Installing Python dependencies..." -ForegroundColor Yellow
pip install -q -r backend/requirements.txt
pip install -q -r graph-generator/requirements.txt
pip install -q -r crm-simulator/requirements.txt
pip install -q -r hub/api/requirements.txt
Write-Host "   ✅ Python dependencies installed" -ForegroundColor Green

# Step 3: Install frontend dependencies
Write-Host "`n📦 Step 3: Installing frontend dependencies..." -ForegroundColor Yellow
Write-Host "--> frontend"
Push-Location frontend; npm install --silent; Pop-Location
Write-Host "--> crm-simulator/frontend"
Push-Location crm-simulator/frontend; npm install --silent; Pop-Location
Write-Host "--> hub"
Push-Location hub; npm install --silent; Pop-Location
Write-Host "   ✅ Frontend dependencies installed" -ForegroundColor Green

# Step 4: Health check
Write-Host "`n✅ Demo environment ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Run .\scripts\start-local.ps1 to start all services"
Write-Host "Or start them individually:"
Write-Host "   1. cd crm-simulator; uvicorn main:app --port 8001"
Write-Host "   2. cd graph-generator; uvicorn main:app --port 8002"
Write-Host "   3. cd backend; uvicorn main:app --port 8000"
Write-Host "   4. cd hub/api; uvicorn main:app --port 8003"
Write-Host "   5. cd frontend; npm run dev"
Write-Host "   6. cd crm-simulator/frontend; npm run dev"
Write-Host "   7. cd hub; npm run dev -- --port 5176"
