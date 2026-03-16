# Synapse — Legacy Infrastructure Cleanup
# Use this to remove orphaned resources after the three-tier rename

param(
    [Parameter(Mandatory = $false)]
    [string]$ProjectId = "synapse-gemini-live",
    
    [Parameter(Mandatory = $false)]
    [string]$Region = "us-central1"
)

Write-Host "🕵️ Checking for orphaned 'voice-ui' or 'frontend' resources..." -ForegroundColor Cyan

# 1. Cloud Run
Write-Host "`n[1/2] Checking Cloud Run services..." -ForegroundColor Yellow
$legacyServices = @("synapse-voice-ui", "synapse-frontend", "voice-ui")

foreach ($svc in $legacyServices) {
    $exists = gcloud run services describe $svc --region $Region --project $ProjectId --format="value(status.url)" 2>$null
    if ($exists) {
        Write-Host "🗑️ Found orphaned service: $svc. Deleting..." -ForegroundColor Red
        gcloud run services delete $svc --region $Region --project $ProjectId --quiet
    } else {
        Write-Host "✅ No service matching '$svc' found." -ForegroundColor DarkGray
    }
}

# 2. Artifact Registry Images
Write-Host "`n[2/2] Checking Artifact Registry for legacy images..." -ForegroundColor Yellow
$legacyImages = @("voice-ui", "frontend")

foreach ($img in $legacyImages) {
    $repoPath = "${Region}-docker.pkg.dev/${ProjectId}/synapse/$img"
    Write-Host "🔍 Checking $repoPath..." -ForegroundColor DarkGray
    # Note: We don't delete images automatically as they are low cost, 
    # but we inform the user.
    $tags = gcloud artifacts docker images list $repoPath --limit=1 --format="value(package)" 2>$null
    if ($tags) {
        Write-Host "📂 Found legacy image repository: $img. Consider manual cleanup to save minimal storage costs." -ForegroundColor Yellow
    }
}

Write-Host "`n✨ Cleanup check complete." -ForegroundColor Green
