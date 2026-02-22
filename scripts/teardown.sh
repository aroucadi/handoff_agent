#!/bin/bash
PROJECT_ID="${1:-handoff-dev}"
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

echo -e "\n\033[33m[1/2] Destroying Terraform Infrastructure...\033[0m"
cd infra
terraform destroy -auto-approve -var="project_id=$PROJECT_ID" -var="region=$REGION"
cd ..

echo -e "\n\033[32m[2/2] Teardown Complete!\033[0m"
