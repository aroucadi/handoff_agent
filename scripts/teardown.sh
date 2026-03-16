#!/bin/bash
# ─────────────────────────────────────────────────────
# Synapse — Infrastructure Teardown (Linux/Bash)
# ─────────────────────────────────────────────────────

set -e

PROJECT_ID="${1:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${2:-us-central1}"

echo -e "\033[31m=============================================\033[0m"
echo -e "\033[31m🗑️ Synapse — Infrastructure Teardown\033[0m"
echo -e "\033[31mProject: $PROJECT_ID | Region: $REGION\033[0m"
echo -e "\033[31m=============================================\033[0m"

echo -e "\033[33mWARNING: This will destroy ALL Cloud Run, Storage, and Firestore resources created by Terraform.\033[0m"
read -p "Are you sure you want to proceed? (yes/no) " confirmation

if [ "$confirmation" != "yes" ]; then
    echo -e "\033[32mAborting teardown.\033[0m"
    exit 0
fi

echo -e "\n\033[33m[1/3] Destroying Terraform Infrastructure...\033[0m"
(cd infra && terraform destroy -auto-approve -var="project_id=$PROJECT_ID" -var="region=$REGION" -var="synapse_admin_key=teardown-dummy")

echo -e "\n\033[33m[2/3] Cleaning up persistent resources via gcloud...\033[0m"

# Cleanup Artifact Registry
echo "--> Checking Artifact Registry 'synapse'..."
if gcloud artifacts repositories describe synapse --location=$REGION --project=$PROJECT_ID --quiet &>/dev/null; then
    echo "!!! Found Artifact Registry. Deleting..."
    gcloud artifacts repositories delete synapse --location=$REGION --project=$PROJECT_ID --quiet
fi

# Cleanup Storage Buckets
BUCKETS=(
    "${PROJECT_ID}-synapse-graphs"
    "${PROJECT_ID}-synapse-uploads"
    "${PROJECT_ID}-knowledge-center"
)

for BUCKET in "${BUCKETS[@]}"; do
    echo "--> Checking bucket: gs://$BUCKET"
    if gcloud storage buckets describe "gs://$BUCKET" --project=$PROJECT_ID --quiet &>/dev/null; then
        echo "!!! Found bucket. Removing..."
        gcloud storage buckets delete "gs://$BUCKET" --project=$PROJECT_ID --quiet
    fi
done

# Cleanup Secrets
echo "--> Checking Secret: gemini-api-key"
if gcloud secrets describe gemini-api-key --project=$PROJECT_ID --quiet &>/dev/null; then
    echo "!!! Found Secret. Deleting..."
    gcloud secrets delete gemini-api-key --project=$PROJECT_ID --quiet
fi

echo -e "\n\033[32m[3/3] Teardown Complete! The project is clean.\033[0m"
