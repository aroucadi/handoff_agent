param(
    [string]$ProjectId = "synapse-488201",
    [string]$Region = "us-central1"
)

$ErrorActionPreference = "Stop"

Write-Host "Building CRM Frontend..." -ForegroundColor Yellow
Push-Location crm-simulator/frontend
npm run build
Pop-Location

$DeployTag = $(Get-Date -Format 'yyyyMMdd-HHmmss')
$Image = "${Region}-docker.pkg.dev/${ProjectId}/synapse/crm-simulator:${DeployTag}"

Write-Host "Building and Pushing CRM Simulator to GCP ($Image)..." -ForegroundColor Yellow
$CloudBuildConfig = @"
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', '$Image', '-f', 'crm-simulator/Dockerfile', '.']
images:
  - '$Image'
"@
$CloudBuildConfig | Out-File -FilePath .cloudbuild-crm-temp.yaml -Encoding utf8 -Force

gcloud builds submit . --config .cloudbuild-crm-temp.yaml --project $ProjectId

Remove-Item .cloudbuild-crm-temp.yaml -Force

Write-Host "Deploying CRM Simulator to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy synapse-crm-simulator --image $Image --region $Region --project $ProjectId --quiet

Write-Host "CRM Simulator Deploy Complete!" -ForegroundColor Green
