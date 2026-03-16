param(
    [Parameter(Mandatory=$false)]
    [string]$ProjectId = $(gcloud config get-value project),
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-central1"
)

Write-Host "=============================================" -ForegroundColor Red
Write-Host "🗑️ Synapse — Infrastructure Teardown" -ForegroundColor Red
Write-Host "Project: $ProjectId | Region: $Region" -ForegroundColor Red
Write-Host "=============================================" -ForegroundColor Red

Write-Host "WARNING: This will destroy ALL Cloud Run, Storage, and Firestore resources created by Terraform." -ForegroundColor Yellow
$confirmation = Read-Host "Are you sure you want to proceed? (yes/no)"
if ($confirmation -ne "yes") {
    Write-Host "Aborting teardown." -ForegroundColor Green
    exit 0
}

Write-Host "`n[1/3] Destroying Terraform Infrastructure..." -ForegroundColor Yellow
Set-Location -Path ./infra
terraform destroy -auto-approve -var="project_id=$ProjectId" -var="region=$Region" -var="synapse_admin_key=teardown-dummy"
Set-Location -Path ..

Write-Host "`n[2/3] Cleaning up persistent resources via gcloud (Self-Sufficiency Check)..." -ForegroundColor Yellow

# Cleanup Artifact Registry
Write-Host "--> Checking Artifact Registry 'synapse'..."
$repoExists = $false
$oldEAP = $ErrorActionPreference
$ErrorActionPreference = "Continue"
& gcloud artifacts repositories describe synapse --location=$Region --project=$ProjectId --format="value(name)" --quiet 2>$null
if ($LASTEXITCODE -eq 0) { $repoExists = $true }
$ErrorActionPreference = $oldEAP

if ($repoExists) {
    Write-Host "!!! Found Artifact Registry. Deleting..." -ForegroundColor Red
    & gcloud artifacts repositories delete synapse --location=$Region --project=$ProjectId --quiet
}

# Cleanup Storage Buckets (if not already gone)
$buckets = @(
    "${ProjectId}-synapse-graphs",
    "${ProjectId}-synapse-uploads",
    "${ProjectId}-knowledge-center"
)

foreach ($bucket in $buckets) {
    Write-Host "--> Checking bucket: gs://$bucket"
    $exists = $false
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & gcloud storage buckets describe gs://$bucket --project=$ProjectId --format="value(name)" --quiet 2>$null
    if ($LASTEXITCODE -eq 0) { $exists = $true }
    $ErrorActionPreference = $oldEAP

    if ($exists) {
        Write-Host "!!! Found bucket. Removing..." -ForegroundColor Red
        & gcloud storage buckets delete gs://$bucket --project=$ProjectId --quiet
    }
}

# Cleanup Secrets
Write-Host "--> Checking Secret: gemini-api-key"
$secretExists = $false
$oldEAP = $ErrorActionPreference
$ErrorActionPreference = "Continue"
& gcloud secrets describe gemini-api-key --project=$ProjectId --format="value(name)" --quiet 2>$null
if ($LASTEXITCODE -eq 0) { $secretExists = $true }
$ErrorActionPreference = $oldEAP

if ($secretExists) {
    Write-Host "!!! Found Secret. Deleting..." -ForegroundColor Red
    & gcloud secrets delete gemini-api-key --project=$ProjectId --quiet
}

Write-Host "`n[3/3] Teardown Complete! The project is clean." -ForegroundColor Green
