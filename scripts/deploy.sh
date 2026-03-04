#!/bin/bash
set -e

PROJECT_ID="${1:-synapse-dev}"
REGION="${2:-us-central1}"
FIREBASE_PROJECT="${3:-$PROJECT_ID}"

echo -e "\033[36m=============================================\033[0m"
echo -e "\033[36m🚀 Synapse — One-Click Terraform Deployment\033[0m"
echo -e "\033[36mProject: $PROJECT_ID | Region: $REGION\033[0m"
echo -e "\033[36m=============================================\033[0m"

# 1. Login verification & Generate Tag
echo -e "\n\033[33m[1/4] Checking gcloud auth & Generating Deploy Tag...\033[0m"
gcloud config set project "$PROJECT_ID" --quiet

DEPLOY_TAG=$(date +%Y%m%d-%H%M%S)
echo "Generated Deploy Tag: $DEPLOY_TAG"

echo -e "\n\033[33m[2/4] Building and Pushing Containers to GCP...\033[0m"

# Build frontends first locally
echo '--> Building SalesClaw CRM Frontend'
(cd crm-simulator/frontend && npm install && npm run build)

echo '--> Building Synapse Hub Frontend'
(cd hub && npm install && npm run build)

echo "--> Submitting Remote Build to Google Cloud Build with tag $DEPLOY_TAG"
gcloud builds submit --config cloudbuild.yaml . --project "$PROJECT_ID" --substitutions "_REGION=$REGION,_TAG=$DEPLOY_TAG"

echo -e "\n\033[33m[3/4] Applying Terraform Infrastructure...\033[0m"
cd infra
terraform init
terraform apply -auto-approve -var="project_id=$PROJECT_ID" -var="region=$REGION"

echo "--> Exporting Terraform Outputs..."
API_URL=$(terraform output -raw api_url)
HUB_URL=$(terraform output -raw hub_url)
WS_URL=$(echo $API_URL | sed 's/^https:\/\//wss:\/\//')

echo "VITE_API_URL=$API_URL" > ../frontend/.env.production
echo "VITE_WS_URL=$WS_URL" >> ../frontend/.env.production
echo "VITE_API_URL=$HUB_URL" > ../hub/.env.production

cd ..

echo "--> Forcing Cloud Run to pull latest image digests..."
gcloud run deploy synapse-api --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/synapse/api:${DEPLOY_TAG} --region $REGION --project $PROJECT_ID --quiet
gcloud run deploy synapse-graph-generator --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/synapse/graph-generator:${DEPLOY_TAG} --region $REGION --project $PROJECT_ID --quiet
gcloud run deploy synapse-crm-simulator --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/synapse/crm-simulator:${DEPLOY_TAG} --region $REGION --project $PROJECT_ID --quiet
gcloud run deploy synapse-hub --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/synapse/hub:${DEPLOY_TAG} --region $REGION --project $PROJECT_ID --quiet

echo -e "\n\033[33m[4/4] Deploying React Voice UI to Firebase...\033[0m"
cd frontend
npm run build
firebase deploy --only hosting --project "$FIREBASE_PROJECT" --non-interactive
cd ..

echo -e "\033[32mDeployment Complete! The Voice Agent is now LIVE.\033[0m"
echo -e "\033[32mCheck output variables from Terraform for URLs.\033[0m"
