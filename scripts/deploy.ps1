param(
    [Parameter(Mandatory = $false)]
    [string]$ProjectId = "synapse-488201",
    
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

# 1. Login verification & Generate Tag
Write-Host "`n[1/4] Checking gcloud auth & Generating Deploy Tag..." -ForegroundColor Yellow
gcloud config set project $ProjectId --quiet

$DeployTag = $(Get-Date -Format 'yyyyMMdd-HHmmss')
Write-Host "Generated Deploy Tag: $DeployTag" -ForegroundColor Cyan

# 2. Build and push containers to GCP (Remote Build)
Write-Host "`n[2/4] Building and Pushing Containers to GCP..." -ForegroundColor Yellow

# Build CRM & Hub Frontends first locally (required for images if hosting assets)
Write-Host '--> Building SalesClaw CRM Frontend'
Push-Location -Path crm-simulator/frontend
npm install
npm run build
Pop-Location

Write-Host '--> Building Synapse Hub Frontend'
Push-Location -Path hub
npm install
npm run build
Pop-Location

Write-Host "--> Submitting Remote Build to Google Cloud Build with tag $DeployTag"
gcloud builds submit --config cloudbuild.yaml . --project $ProjectId --substitutions "_REGION=$Region,_TAG=$DeployTag"
if ($LASTEXITCODE -ne 0) { throw "Cloud Build failed with exit code $LASTEXITCODE" }

# 3. Apply Terraform
Write-Host "`n[3/4] Applying Terraform Infrastructure..." -ForegroundColor Yellow
Set-Location -Path ./infra
terraform init
terraform apply -auto-approve -var="project_id=$ProjectId" -var="region=$Region"

Write-Host "--> Exporting Terraform Outputs..." -ForegroundColor Yellow
$apiUrl = terraform output -raw api_url
$hubUrl = terraform output -raw hub_url
$wsUrl = $apiUrl -replace "^https://", "wss://"

$envContent = "VITE_API_URL=$apiUrl`nVITE_WS_URL=$wsUrl`nVITE_HUB_URL=$hubUrl"
Set-Content -Path ../frontend/.env.production -Value $envContent

# Hub also needs its production API URL
$hubEnv = "VITE_API_URL=$hubUrl"
Set-Content -Path ../hub/.env.production -Value $hubEnv

Set-Location -Path ..

Write-Host "--> Forcing Cloud Run to pull latest image digests..." -ForegroundColor Yellow
gcloud run deploy synapse-api --image ${Region}-docker.pkg.dev/${ProjectId}/synapse/api:${DeployTag} --region $Region --project $ProjectId --quiet
gcloud run deploy synapse-graph-generator --image ${Region}-docker.pkg.dev/${ProjectId}/synapse/graph-generator:${DeployTag} --region $Region --project $ProjectId --quiet
gcloud run deploy synapse-crm-simulator --image ${Region}-docker.pkg.dev/${ProjectId}/synapse/crm-simulator:${DeployTag} --region $Region --project $ProjectId --quiet
gcloud run deploy synapse-hub --image ${Region}-docker.pkg.dev/${ProjectId}/synapse/hub:${DeployTag} --region $Region --project $ProjectId --quiet

# 4. Deploy Frontend
Write-Host "`n[4/4] Deploying React Voice UI to Firebase..." -ForegroundColor Yellow
Set-Location -Path ./frontend
npm install
npm run build

if (Get-Command firebase -ErrorAction SilentlyContinue) {
    firebase deploy --only hosting --project $FirebaseProject --non-interactive
} else {
    Write-Host "⚠️ Global Firebase CLI not found. Trying npx..." -ForegroundColor Yellow
    npx -y firebase-tools deploy --only hosting --project $FirebaseProject --non-interactive
}
Set-Location -Path ..

Write-Host -Object 'Deployment Complete! The Voice Agent is now LIVE.' -ForegroundColor Green
Write-Host -Object 'Check output variables from Terraform for URLs.' -ForegroundColor Green
