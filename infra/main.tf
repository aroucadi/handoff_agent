# Synapse — Terraform Main Configuration

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }

  # Uncomment after creating the state bucket:
  # backend "gcs" {
  #   bucket = "YOUR_PROJECT_ID-terraform-state"
  #   prefix = "terraform/state"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# ---------------------------------------------------------------------------
# Enable required GCP APIs
# ---------------------------------------------------------------------------
# resource "google_project_service" "apis" {
#   for_each = toset([
#     "run.googleapis.com",
#     "firestore.googleapis.com",
#     "storage.googleapis.com",
#     "aiplatform.googleapis.com",
#     "secretmanager.googleapis.com",
#     "cloudbuild.googleapis.com",
#     "firebase.googleapis.com",
#     "generativelanguage.googleapis.com",
#     "artifactregistry.googleapis.com",
#   ])
#   project            = var.project_id
#   service            = each.value
#   disable_on_destroy = false
# }

# ---------------------------------------------------------------------------
# Secret Manager — Gemini API Key
# ---------------------------------------------------------------------------
resource "google_secret_manager_secret" "gemini_key" {
  secret_id = "gemini-api-key"
  project   = var.project_id

  replication {
    auto {}
  }

  # depends_on = [google_project_service.apis]
}

# ---------------------------------------------------------------------------
# Modules
# ---------------------------------------------------------------------------
module "storage" {
  source      = "./modules/storage"
  project_id  = var.project_id
  region      = var.region
  environment = var.environment

  # depends_on = [google_project_service.apis]
}

module "firestore" {
  source     = "./modules/firestore"
  project_id = var.project_id
  region     = var.region

  # depends_on = [google_project_service.apis]
}

module "cloud_run" {
  source              = "./modules/cloud-run"
  project_id          = var.project_id
  region              = var.region
  skill_graphs_bucket = module.storage.skill_graphs_bucket_name
  uploads_bucket      = module.storage.uploads_bucket_name
  synapse_admin_key   = var.synapse_admin_key

  depends_on = [module.storage, module.firestore]
}

# module "firebase" {
#   source     = "./modules/firebase"
#   project_id = var.project_id
# 
#   # depends_on = [google_project_service.apis]
# }
