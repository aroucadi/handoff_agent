# Synapse — Start Local Development Environment (Windows)
# Starts all services in the background and tracks PIDs for cleanup

$ErrorActionPreference = "Stop"

Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      SYNAPSE — Starting All Services         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$ROOT_DIR = Get-Item $PSScriptRoot\..

# Function to start a process and return its ID
function Start-SynapseProcess {
    param($Name, $Cwd, $Command, $Args)
    Write-Host "🚀 Starting $Name..." -ForegroundColor Yellow
    $p = Start-Process -FilePath $Command -ArgumentList $Args -WorkingDirectory $Cwd -PassThru -NoNewWindow
    return $p.Id
}

$PIDs = @()

# 1. CRM Simulator Backend
$PIDs += Start-SynapseProcess "CRM Backend (:8001)" "$ROOT_DIR\crm-simulator" "uvicorn" "main:app --host 0.0.0.0 --port 8001"

# 2. Graph Generator
$PIDs += Start-SynapseProcess "Graph Generator (:8002)" "$ROOT_DIR\graph-generator" "uvicorn" "main:app --host 0.0.0.0 --port 8002"

# 3. Synapse API
$PIDs += Start-SynapseProcess "Synapse API (:8000)" "$ROOT_DIR\backend" "uvicorn" "main:app --host 0.0.0.0 --port 8000"

# 4. Hub API
$PIDs += Start-SynapseProcess "Hub API (:8003)" "$ROOT_DIR\hub\api" "uvicorn" "main:app --host 0.0.0.0 --port 8003"

# 5. CRM Frontend
$PIDs += Start-SynapseProcess "CRM Frontend (:5173)" "$ROOT_DIR\crm-simulator\frontend" "npm" "run dev"

# 6. Synapse Live Agent UI
$PIDs += Start-SynapseProcess "Live Agent UI (:5174)" "$ROOT_DIR\live-agent" "npm" "run dev"

# 7. Synapse Hub UI
$PIDs += Start-SynapseProcess "Hub UI (:5176)" "$ROOT_DIR\hub" "npm" "run dev -- --port 5176"

# 8. Synapse Admin Portal UI
$PIDs += Start-SynapseProcess "Admin UI (:5177)" "$ROOT_DIR\admin-portal" "npm" "run dev -- --port 5177"

Write-Host ""
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  All services started!"
Write-Host ""
Write-Host "  🏢 CRM Simulator:   http://localhost:5173"
Write-Host "  🎙️ Synapse Live:    http://localhost:5174"
Write-Host "  🌉 Synapse Hub:      http://localhost:5176"
Write-Host "  👑 Synapse Admin:    http://localhost:5177"
Write-Host "  📡 Backend API:      http://localhost:8000/health"
Write-Host "  ⚙️  Graph Generator:  http://localhost:8002/health"
Write-Host "  🛠️  Hub API:         http://localhost:8003/docs"
Write-Host "  🛡️  Admin API:       http://localhost:8004/docs"
Write-Host ""
Write-Host "  Press Ctrl+C to stop all services (Wait for cleanup)"
Write-Host "═══════════════════════════════════════════════"

# Keep the script running and catch Ctrl+C
try {
    while ($true) { Start-Sleep -Seconds 1 }
}
finally {
    Write-Host "`nStopping all services..." -ForegroundColor Red
    foreach ($id in $PIDs) {
        Stop-Process -Id $id -ErrorAction SilentlyContinue
    }
    Write-Host "All services stopped."
}
