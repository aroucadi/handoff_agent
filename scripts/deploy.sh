#!/bin/bash
set -e

PROJECT_ID="${1:-handoff-dev}"
REGION="${2:-us-central1}"
FIREBASE_PROJECT="${3:-$PROJECT_ID}"

echo -e "\033[36m=============================================\033[0m"
echo -e "\033[36m🚀 Synapse — One-Click Terraform Deployment\033[0m"
echo -e "\033[36mProject: $PROJECT_ID | Region: $REGION\033[0m"
echo -e "\033[36m=============================================\033[0m"

echo -e "\n\033[33m[1/4] Checking gcloud auth...\033[0m"
gcloud config set project "$PROJECT_ID"

echo -e "\n\033[33m[2/4] Building and Pushing Containers to GCP...\033[0m"
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

echo '--> Building Backend API'
docker build -f backend/Dockerfile -t "${REGION}-docker.pkg.dev/${PROJECT_ID}/synapse/api:latest" .
docker push "${REGION}-docker.pkg.dev/${PROJECT_ID}/synapse/api:latest"

echo '--> Building Graph Generator'
docker build -f graph-generator/Dockerfile -t "${REGION}-docker.pkg.dev/${PROJECT_ID}/synapse/graph-generator:latest" .
docker push "${REGION}-docker.pkg.dev/${PROJECT_ID}/synapse/graph-generator:latest"

echo '--> Building CRM Simulator'
docker build -f crm-simulator/Dockerfile -t "${REGION}-docker.pkg.dev/${PROJECT_ID}/synapse/crm-simulator:latest" .
docker push "${REGION}-docker.pkg.dev/${PROJECT_ID}/synapse/crm-simulator:latest"

echo -e "\n\033[33m[3/4] Applying Terraform Infrastructure...\033[0m"
cd infra
terraform init
terraform apply -auto-approve -var="project_id=$PROJECT_ID" -var="region=$REGION"
cd ..

echo -e "\n\033[33m[4/4] Deploying React Voice UI to Firebase...\033[0m"
cd frontend
npm run build
firebase deploy --only hosting --project "$FIREBASE_PROJECT" --non-interactive
cd ..

echo -e "\033[32mDeployment Complete! The Voice Agent is now LIVE.\033[0m"
echo -e "\033[32mCheck output variables from Terraform for URLs.\033[0m"
