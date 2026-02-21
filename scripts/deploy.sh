#!/bin/bash
# ─────────────────────────────────────────────────────
# Handoff — Cloud Deploy Script
#
# Builds and deploys all services to Cloud Run.
# Requires: gcloud CLI, Docker, Terraform
# ─────────────────────────────────────────────────────

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║       HANDOFF — Cloud Deployment             ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

PROJECT_ID="${PROJECT_ID:?PROJECT_ID is required}"
REGION="${REGION:-us-central1}"
REPO="${REGION}-docker.pkg.dev/${PROJECT_ID}/handoff"

echo "📋 Configuration:"
echo "   PROJECT_ID: $PROJECT_ID"
echo "   REGION:     $REGION"
echo "   REPO:       $REPO"
echo ""

# Step 1: Terraform
echo "🏗️  Step 1: Applying Terraform infrastructure..."
cd infra
terraform init
terraform apply -auto-approve \
    -var="project_id=${PROJECT_ID}" \
    -var="region=${REGION}" \
    -var="environment=production"
cd ..
echo "   ✅ Infrastructure ready"

# Step 2: Build and push API image
echo ""
echo "🐳 Step 2: Building Handoff API image..."
docker build -t "${REPO}/api:latest" backend/
docker push "${REPO}/api:latest"
echo "   ✅ API image pushed"

# Step 3: Build and push Graph Generator image
echo ""
echo "🐳 Step 3: Building Graph Generator image..."
docker build -t "${REPO}/graph-generator:latest" graph-generator/
docker push "${REPO}/graph-generator:latest"
echo "   ✅ Graph Generator image pushed"

# Step 4: Build frontend
echo ""
echo "📦 Step 4: Building frontend..."
cd frontend
npm ci
npm run build
cd ..
echo "   ✅ Frontend built"

# Step 5: Deploy Cloud Run services
echo ""
echo "🚀 Step 5: Deploying Cloud Run services..."
gcloud run services update handoff-api \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --image="${REPO}/api:latest"

gcloud run services update handoff-graph-generator \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --image="${REPO}/graph-generator:latest"

echo "   ✅ Cloud Run services deployed"

# Step 6: Seed static graphs
echo ""
echo "📚 Step 6: Seeding static skill graphs..."
bash scripts/seed-graphs.sh
echo "   ✅ Static graphs seeded"

echo ""
echo "═══════════════════════════════════════════════"
echo "  Deployment complete!"
echo ""
echo "  API URL:       $(terraform -chdir=infra output -raw api_url)"
echo "  Generator URL: $(terraform -chdir=infra output -raw graph_generator_url)"
echo "═══════════════════════════════════════════════"
