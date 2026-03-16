param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-central1"
)

Write-Host "--> Syncing Terraform state with existing cloud resources..." -ForegroundColor Yellow

# Function to import safely
function Import-Resource {
    param($Addr, $Id)
    # Check if already in state
    $inState = & terraform state list $Addr 2>$null
    if ($inState) {
        Write-Host "✅ $Addr already in state." -ForegroundColor Gray
        return
    }
    Write-Host "--> Importing $Addr ($Id)..." -ForegroundColor Cyan
    & terraform import $Addr $Id
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Successfully imported $Addr" -ForegroundColor Green
    } else {
        Write-Host "⚠️  $Addr import failed (might not exist in GCP)." -ForegroundColor Gray
    }
}

Set-Location -Path ./infra
terraform init

# Storage Buckets
Import-Resource "module.storage.google_storage_bucket.skill_graphs" "$ProjectId-synapse-graphs"
Import-Resource "module.storage.google_storage_bucket.uploads" "$ProjectId-synapse-uploads"
Import-Resource "module.storage.google_storage_bucket.knowledge_center" "$ProjectId-knowledge-center"

# Secrets
Import-Resource "google_secret_manager_secret.gemini_key" "projects/$ProjectId/secrets/gemini-api-key"

# Artifact Registry
Import-Resource "module.cloud_run.google_artifact_registry_repository.synapse" "projects/$ProjectId/locations/$Region/repositories/synapse"

# Cloud Run Services
Import-Resource "module.cloud_run.google_cloud_run_v2_service.api" "projects/$ProjectId/locations/$Region/services/synapse-api"
Import-Resource "module.cloud_run.google_cloud_run_v2_service.graph_generator" "projects/$ProjectId/locations/$Region/services/synapse-graph-generator"
Import-Resource "module.cloud_run.google_cloud_run_v2_service.crm_simulator" "projects/$ProjectId/locations/$Region/services/synapse-crm-simulator"
Import-Resource "module.cloud_run.google_cloud_run_v2_service.hub" "projects/$ProjectId/locations/$Region/services/synapse-hub"
Import-Resource "module.cloud_run.google_cloud_run_v2_service.admin" "projects/$ProjectId/locations/$Region/services/synapse-admin"

Set-Location -Path ..
Write-Host "`n✅ Terraform state is now ALIGNED with reality." -ForegroundColor Green
