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

Write-Host '--> Building Synapse Admin Portal Frontend'
Push-Location -Path admin-portal
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

Write-Host "---> Exporting Terraform Outputs..." -ForegroundColor Yellow
$apiUrl = terraform output -raw api_url
$hubUrl = terraform output -raw hub_url
$adminUrl = terraform output -raw admin_url
$wsUrl = $apiUrl -replace "^https://", "wss://"

# Voice UI is hosted on Firebase Hosting — resolve URL from project ID
$voiceUiUrl = "https://${FirebaseProject}.web.app"

$liveAgentEnv = "VITE_API_URL=$apiUrl`nVITE_WS_URL=$wsUrl`nVITE_HUB_URL=$hubUrl"
Set-Content -Path ../live-agent/.env.production -Value $liveAgentEnv

# Hub needs its own API URL + the Live Agent URL for 'Launch Agent' button
$hubEnv = "VITE_API_URL=$hubUrl`nVITE_VOICE_UI_URL=$voiceUiUrl"
Set-Content -Path ../hub/.env.production -Value $hubEnv

# Admin Portal env
$adminEnv = "VITE_API_URL=$adminUrl`nVITE_HUB_URL=$hubUrl"
Set-Content -Path ../admin-portal/.env.production -Value $adminEnv

Set-Location -Path ..

Write-Host "--> Forcing Cloud Run to pull latest image digests..." -ForegroundColor Yellow
gcloud run deploy synapse-api --image ${Region}-docker.pkg.dev/${ProjectId}/synapse/api:${DeployTag} --region $Region --project $ProjectId --quiet
gcloud run deploy synapse-graph-generator --image ${Region}-docker.pkg.dev/${ProjectId}/synapse/graph-generator:${DeployTag} --region $Region --project $ProjectId --quiet
gcloud run deploy synapse-crm-simulator --image ${Region}-docker.pkg.dev/${ProjectId}/synapse/crm-simulator:${DeployTag} --region $Region --project $ProjectId --quiet
gcloud run deploy synapse-hub --image ${Region}-docker.pkg.dev/${ProjectId}/synapse/hub:${DeployTag} --region $Region --project $ProjectId --quiet
gcloud run deploy synapse-admin --image ${Region}-docker.pkg.dev/${ProjectId}/synapse/admin:${DeployTag} --region $Region --project $ProjectId --quiet

# 4. Deploy ClawdView Knowledge Center to GCS Static Site
Write-Host "`n[4/5] Syncing ClawdView Knowledge Center to GCS..." -ForegroundColor Yellow
$kcBucket = "${ProjectId}-knowledge-center"

Write-Host "---> Syncing knowledge-center/ to gs://${kcBucket}"
gcloud storage rsync knowledge-center/ "gs://${kcBucket}" --recursive --delete-unmatched-destination-objects

$kcUrl = "https://storage.googleapis.com/${kcBucket}/index.html"
Write-Host "---> Knowledge Center deployed at: $kcUrl" -ForegroundColor Green

# 5. Deploy Live Agent
Write-Host "`n[5/5] Deploying React Live Agent to Firebase..." -ForegroundColor Yellow
Set-Location -Path ./live-agent
npm install
npm run build

if (Get-Command firebase -ErrorAction SilentlyContinue) {
    firebase deploy --only hosting --project $FirebaseProject --non-interactive
} else {
    Write-Host "⚠️ Global Firebase CLI not found. Trying npx..." -ForegroundColor Yellow
    npx -y firebase-tools deploy --only hosting --project $FirebaseProject --non-interactive
}
Set-Location -Path ..

Write-Host -Object 'Deployment Complete! The Synapse Suite is now LIVE.' -ForegroundColor Green
Write-Host -Object "Admin Portal URL: $adminUrl" -ForegroundColor Green
Write-Host -Object "Hub URL: $hubUrl" -ForegroundColor Green
Write-Host -Object "Live Agent URL: ${voiceUiUrl}/t/gemini-live-hackathon/voice" -ForegroundColor Green
Write-Host -Object 'Check output variables from Terraform for URLs.' -ForegroundColor Green

# 6. Run Integrated System Test
Write-Host "`n[6/6] Verifying Data Pipelines Architecture & Event Handlers..." -ForegroundColor Yellow
$crmUrlDeployed = gcloud run services describe synapse-crm-simulator --region $Region --format "value(status.url)"
if ($crmUrlDeployed) {
    $graphUrlDeployed = gcloud run services describe synapse-graph-generator --region $Region --format "value(status.url)"
    Write-Host "---> Found CRM URL: $crmUrlDeployed"
    Write-Host "---> Found Graph URL: $graphUrlDeployed"
    py scripts/test_pipeline.py --crm_url $crmUrlDeployed --graph_url $graphUrlDeployed
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Integration Test Failed! The pipeline might be broken." -ForegroundColor Red
        exit $LASTEXITCODE
    } else {
        Write-Host "✅ Pipeline End-to-End Governance Tested Successfully!" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️ Could not resolve CRM Simulator URL for testing." -ForegroundColor Yellow
}
