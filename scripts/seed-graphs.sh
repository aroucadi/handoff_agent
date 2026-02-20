#!/bin/bash
# Seed pre-built skill graphs to GCS
# Usage: ./scripts/seed-graphs.sh <PROJECT_ID> [REGION]

set -e

PROJECT_ID=${1:?"Usage: $0 <PROJECT_ID> [REGION]"}
REGION=${2:-"us-central1"}
BUCKET="${PROJECT_ID}-skill-graphs"

echo "📚 Seeding skill graphs to gs://${BUCKET}/"
echo ""

# Upload product layer
echo "📦 Uploading product knowledge layer..."
gsutil -m cp -r skill-graphs/product/ "gs://${BUCKET}/product/"
echo "   ✅ Product layer uploaded"

# Upload industry layer
echo "🏭 Uploading industry knowledge layer..."
gsutil -m cp -r skill-graphs/industries/ "gs://${BUCKET}/industries/"
echo "   ✅ Industry layer uploaded"

# Verify
echo ""
echo "📊 Verification:"
echo "   Product nodes:"
gsutil ls "gs://${BUCKET}/product/" | wc -l
echo "   Industry nodes:"
gsutil ls -r "gs://${BUCKET}/industries/" | grep "\.md$" | wc -l

echo ""
echo "✅ Skill graphs seeded successfully!"
