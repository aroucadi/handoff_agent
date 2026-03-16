#!/bin/bash
# ─────────────────────────────────────────────────────
# Synapse — Demo Setup Script
#
# Seeds static skill graphs and validates environment.
# Run this before starting the demo.
# ─────────────────────────────────────────────────────

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║        SYNAPSE — Demo Environment Setup      ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Check required env vars
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY not set. Export it first:"
    echo "   export GEMINI_API_KEY='your-key-here'"
    exit 1
fi

if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")
fi

if [ -z "$PROJECT_ID" ]; then
    echo "❌ PROJECT_ID not set and could not be resolved from gcloud. Export it first:"
    echo "   export PROJECT_ID='your-project-id'"
    exit 1
fi

BUCKET="${SKILL_GRAPHS_BUCKET:-${PROJECT_ID}-synapse-graphs}"

echo "📋 Configuration:"
echo "   PROJECT_ID: $PROJECT_ID"
echo "   BUCKET:     $BUCKET"
echo ""

# Step 1: Upload static skill graphs
echo "📦 Step 1: Uploading static skill graphs..."
if command -v gsutil &> /dev/null; then
    gsutil -m cp -r skill-graphs/product/* "gs://${BUCKET}/product/"
    gsutil -m cp -r skill-graphs/industries/* "gs://${BUCKET}/industries/"
    echo "   ✅ Static graphs uploaded to GCS"
else
    echo "   ⚠️  gsutil not found — skipping GCS upload (graphs available locally)"
fi

# Step 2: Install Python dependencies
echo ""
echo "🐍 Step 2: Installing Python dependencies..."
pip install -q -r backend/requirements.txt
pip install -q -r graph-generator/requirements.txt
pip install -q -r crm-simulator/requirements.txt
pip install -q -r hub/api/requirements.txt
echo "   ✅ Python dependencies installed"

# Step 3: Install frontend dependencies
echo ""
echo "📦 Step 3: Installing frontend dependencies..."
(cd frontend && npm install --silent)
(cd crm-simulator/frontend && npm install --silent)
(cd hub && npm install --silent)
echo "   ✅ Frontend dependencies installed"

# Step 4: Health check
echo ""
echo "✅ Demo environment ready!"
echo ""
echo "Run ./scripts/start-local.ps1 (Windows) or ./scripts/start-local.sh (Linux) to start all services"
echo "Or start them individually:"
echo "   1. cd crm-simulator && uvicorn main:app --port 8001"
echo "   2. cd graph-generator && uvicorn main:app --port 8002"
echo "   3. cd backend && uvicorn main:app --port 8000"
echo "   4. cd hub/api && uvicorn main:app --port 8003"
echo "   5. cd frontend && npm run dev"
echo "   6. cd crm-simulator/frontend && npm run dev"
echo "   7. cd hub && npm run dev -- --port 5176"
