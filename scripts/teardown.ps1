param(
    [Parameter(Mandatory=$false)]
    [string]$ProjectId = "handoff-dev",
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-central1"
)

Write-Host "=============================================" -ForegroundColor Red
Write-Host "🗑️ Handoff — Infrastructure Teardown" -ForegroundColor Red
Write-Host "Project: $ProjectId | Region: $Region" -ForegroundColor Red
Write-Host "=============================================" -ForegroundColor Red

Write-Host "WARNING: This will destroy ALL Cloud Run, Storage, and Firestore resources created by Terraform." -ForegroundColor Yellow
$confirmation = Read-Host "Are you sure you want to proceed? (yes/no)"
if ($confirmation -ne "yes") {
    Write-Host "Aborting teardown." -ForegroundColor Green
    exit 0
}

Write-Host "`n[1/2] Destroying Terraform Infrastructure..." -ForegroundColor Yellow
Set-Location -Path ./infra
terraform destroy -auto-approve -var="project_id=$ProjectId" -var="region=$Region"
Set-Location -Path ..

Write-Host "`n[2/2] Teardown Complete!" -ForegroundColor Green
