param(
    [Parameter(Mandatory = $false)]
    [string]$ProjectId = "synapse-dev",
    
    [Parameter(Mandatory = $false)]
    [string]$Region = "us-central1",

    [Parameter(Mandatory = $false)]
    [string]$FirebaseProject = $null
)

if (-not $FirebaseProject) {
    $FirebaseProject = $ProjectId
}

$ErrorActionPreference = "Stop"

Write-Host '=============================================' -ForegroundColor Cyan
Write-Host '🚀 Synapse — One-Click Terraform Deployment' -ForegroundColor Cyan
Write-Host "Project: $ProjectId | Region: $Region" -ForegroundColor Cyan
Write-Host '=============================================' -ForegroundColor Cyan

# 1. Login verification
Write-Host "`n[1/4] Checking gcloud auth..." -ForegroundColor Yellow
gcloud config set project $ProjectId

# 2. Build and push containers to Artifact Registry
Write-Host "`n[2/4] Building and Pushing Containers to GCP..." -ForegroundColor Yellow
gcloud auth configure-docker ${Region}-docker.pkg.dev --quiet

# Build CRM Frontend first
Write-Host '--> Building SalesClaw CRM Frontend'
Push-Location -Path crm-simulator/frontend
npm install
npm run build
Pop-Location

# Push API
Write-Host '--> Building Backend API'
docker build -f backend/Dockerfile -t ${Region}-docker.pkg.dev/${ProjectId}/synapse/api:latest .
docker push ${Region}-docker.pkg.dev/${ProjectId}/synapse/api:latest

# Push Graph Generator
Write-Host '--> Building Graph Generator'
docker build -f graph-generator/Dockerfile -t ${Region}-docker.pkg.dev/${ProjectId}/synapse/graph-generator:latest .
docker push ${Region}-docker.pkg.dev/${ProjectId}/synapse/graph-generator:latest

# Push CRM Simulator
Write-Host '--> Building CRM Simulator'
docker build -f crm-simulator/Dockerfile -t ${Region}-docker.pkg.dev/${ProjectId}/synapse/crm-simulator:latest .
docker push ${Region}-docker.pkg.dev/${ProjectId}/synapse/crm-simulator:latest

# 3. Apply Terraform
Write-Host "`n[3/4] Applying Terraform Infrastructure..." -ForegroundColor Yellow
Set-Location -Path ./infra
terraform init
terraform apply -auto-approve -var="project_id=$ProjectId" -var="region=$Region"
Set-Location -Path ..

# 4. Deploy Frontend
Write-Host "`n[4/4] Deploying React Voice UI to Firebase..." -ForegroundColor Yellow
if (Get-Command firebase -ErrorAction SilentlyContinue) {
    Set-Location -Path ./frontend
    npm run build
    firebase deploy --only hosting --project $FirebaseProject --non-interactive
    Set-Location -Path ..
} else {
    Write-Host "⚠️ Firebase CLI not found. Skipping frontend deployment. Please deploy manually or install the CLI." -ForegroundColor Yellow
}

Write-Host -Object 'Deployment Complete! The Voice Agent is now LIVE.' -ForegroundColor Green
Write-Host -Object 'Check output variables from Terraform for URLs.' -ForegroundColor Green
