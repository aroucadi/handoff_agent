param(
    [Parameter(Mandatory = $false)]
    [string]$ProjectId,

    [Parameter(Mandatory = $false)]
    [string]$Region = 'us-central1'
)

$ErrorActionPreference = 'Stop'

Write-Host '=============================================' -ForegroundColor Cyan
Write-Host 'Synapse -- Master Seeding Orchestrator' -ForegroundColor Cyan
Write-Host '=============================================' -ForegroundColor Cyan

# 1. Resolve Project ID
if (-not $ProjectId) {
    if ($env:PROJECT_ID) {
        $ProjectId = $env:PROJECT_ID
    } else {
        $ProjectId = & gcloud config get-value project 2>$null
    }
}

if (-not $ProjectId) {
    Write-Host 'Error: Could not resolve PROJECT_ID.' -ForegroundColor Red
    exit 1
}
Write-Host "Target Project: $ProjectId" -ForegroundColor Cyan

# 2. Check Prerequisites
if (-not $env:SYNAPSE_ADMIN_KEY) {
    Write-Host 'Error: SYNAPSE_ADMIN_KEY environment variable is not set.' -ForegroundColor Red
    exit 1
}

# 3. Resolve Service URLs
Write-Host 'Step 1: Resolving Cloud Run Service URLs...' -ForegroundColor Yellow
function Get-RunUrl {
    param($Service)
    $url = & gcloud run services describe $Service --region $Region --project $ProjectId --format 'value(status.url)' 2>$null
    return $url
}

$api_url = Get-RunUrl 'synapse-api'
$crm_url = Get-RunUrl 'synapse-crm-simulator'
$hub_url = Get-RunUrl 'synapse-hub'
$admin_url = Get-RunUrl 'synapse-admin'
$graph_url = Get-RunUrl 'synapse-graph-generator'

if (-not ($api_url -and $crm_url -and $hub_url -and $admin_url -and $graph_url)) {
    Write-Host 'Error: One or more services not found.' -ForegroundColor Red
    exit 1
}

Write-Host 'Fleet Detected.' -ForegroundColor Green

# 4. Execute Seeding Engine
Write-Host 'Step 2: Executing Seeding Engine...' -ForegroundColor Yellow
$env:PROJECT_ID = $ProjectId
py scripts/seed_all.py --api_url $api_url --crm_url $crm_url --hub_url $hub_url --admin_url $admin_url --graph_url $graph_url

if ($LASTEXITCODE -ne 0) {
    Write-Host 'Error: Seeding failed.' -ForegroundColor Red
    exit $LASTEXITCODE
}

# 5. Final Verification
Write-Host 'Step 3: Verification...' -ForegroundColor Yellow
py scripts/check_graphs.py

Write-Host '=============================================' -ForegroundColor Green
Write-Host 'Seeding Complete!' -ForegroundColor Green
Write-Host '=============================================' -ForegroundColor Green
