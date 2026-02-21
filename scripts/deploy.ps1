param(
    [Parameter(Mandatory=$false)]
    [string]$ProjectId = "handoff-dev",
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-central1"
)

$ErrorActionPreference = "Stop"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "🚀 Handoff — One-Click Terraform Deployment" -ForegroundColor Cyan
Write-Host "Project: $ProjectId | Region: $Region" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 1. Login verification
Write-Host "`n[1/4] Checking gcloud auth..." -ForegroundColor Yellow
gcloud config set project $ProjectId

# 2. Build and push containers to Artifact Registry
Write-Host "`n[2/4] Building and Pushing Containers to GCP..." -ForegroundColor Yellow
gcloud auth configure-docker ${Region}-docker.pkg.dev

# Push API
Write-Host "--> Building Backend API"
docker build -t ${Region}-docker.pkg.dev/${ProjectId}/handoff/api:latest ./backend
docker push ${Region}-docker.pkg.dev/${ProjectId}/handoff/api:latest

# Push Graph Generator
Write-Host "--> Building Graph Generator"
docker build -t ${Region}-docker.pkg.dev/${ProjectId}/handoff/graph-generator:latest ./graph-generator
docker push ${Region}-docker.pkg.dev/${ProjectId}/handoff/graph-generator:latest

# Push CRM Simulator
Write-Host "--> Building CRM Simulator"
docker build -t ${Region}-docker.pkg.dev/${ProjectId}/handoff/crm-simulator:latest ./crm-simulator
docker push ${Region}-docker.pkg.dev/${ProjectId}/handoff/crm-simulator:latest

# 3. Apply Terraform
Write-Host "`n[3/4] Applying Terraform Infrastructure..." -ForegroundColor Yellow
Set-Location -Path ./infra
Initialize-Terraform:
terraform init

Apply-Terraform:
terraform apply -auto-approve -var="project_id=$ProjectId" -var="region=$Region"
Set-Location -Path ..

# 4. Deploy Frontend
Write-Host "`n[4/4] Deploying React Voice UI to Firebase..." -ForegroundColor Yellow
Set-Location -Path ./frontend
npm run build
firebase deploy --only hosting --project $ProjectId
Set-Location -Path ..

Write-Host "`n✅ Deployment Complete! The Voice Agent is now LIVE." -ForegroundColor Green
Write-Host "Check output variables from Terraform for URLs." -ForegroundColor Green
