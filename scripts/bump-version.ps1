param()

$ErrorActionPreference = "Stop"

# 1. Read the global version from synapse.yaml
$ManifestPath = "synapse.yaml"
if (-not (Test-Path $ManifestPath)) {
    Write-Error "Could not find $ManifestPath at root."
    exit 1
}

# Extremely light YAML parser to find global_version
$GlobalVersion = $null
foreach ($line in Get-Content $ManifestPath) {
    if ($line -match "^global_version:\s*(.+)$") {
        $GlobalVersion = $matches[1].Trim()
        break
    }
}

if (-not $GlobalVersion) {
    Write-Error "Could not parse 'global_version' from synapse.yaml"
    exit 1
}

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "🔄 Disseminating Global Version: v$GlobalVersion" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 2. Update React Frontend (package.json)
$PackageJsonPath = "frontend/package.json"
if (Test-Path $PackageJsonPath) {
    Write-Host "-> Updating frontend/package.json"
    $Json = Get-Content $PackageJsonPath | ConvertFrom-Json
    $Json.version = $GlobalVersion
    $Json | ConvertTo-Json -Depth 10 | Set-Content $PackageJsonPath -Encoding UTF8
}

# 3. Helper to update FastAPI main.py versions
function Update-FastAPIVersion {
    param([string]$FilePath)
    if (Test-Path $FilePath) {
        Write-Host "-> Updating $FilePath"
        $Content = Get-Content $FilePath
        # Regex replaces the version="..." kwarg inside FastAPI() instantiation
        $NewContent = $Content -replace 'version="[^"]+"', "version=`"$GlobalVersion`""
        Set-Content -Path $FilePath -Value $NewContent -Encoding UTF8
    }
}

# 4. Update Backend Services
Update-FastAPIVersion "backend/main.py"
Update-FastAPIVersion "graph-generator/main.py"
Update-FastAPIVersion "crm-simulator/main.py"

Write-Host "`n✅ Successfully synchronized all monorepo pieces to v$GlobalVersion." -ForegroundColor Green
Write-Host "Don't forget to push a git tag for v$GlobalVersion!" -ForegroundColor Yellow
