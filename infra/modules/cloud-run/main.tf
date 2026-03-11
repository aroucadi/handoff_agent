# Cloud Run Services for Synapse

# Artifact Registry repository for container images
resource "google_artifact_registry_repository" "synapse" {
  location      = var.region
  repository_id = "synapse"
  format        = "DOCKER"
  project       = var.project_id
}

# Service Account for Cloud Run services
resource "google_service_account" "synapse_runner" {
  account_id   = "synapse-runner"
  display_name = "Synapse Cloud Run Service Account"
  project      = var.project_id
}

# IAM: Cloud Run SA → GCS
resource "google_project_iam_member" "runner_gcs" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.synapse_runner.email}"
}

# IAM: Cloud Run SA → Firestore
resource "google_project_iam_member" "runner_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.synapse_runner.email}"
}

# IAM: Cloud Run SA → Secret Manager
resource "google_project_iam_member" "runner_secrets" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.synapse_runner.email}"
}

# IAM: Cloud Run SA → Vertex AI
resource "google_project_iam_member" "runner_vertexai" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.synapse_runner.email}"
}

# ── Cloud Run: Synapse API ──────────────────────────────────────

resource "google_cloud_run_v2_service" "api" {
  name     = "synapse-api"
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.synapse_runner.email

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/synapse/api:latest"

      ports {
        container_port = 8000
      }

      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "REGION"
        value = var.region
      }
      env {
        name  = "SKILL_GRAPHS_BUCKET"
        value = var.skill_graphs_bucket
      }
      env {
        name  = "UPLOADS_BUCKET"
        value = var.uploads_bucket
      }
      env {
        name  = "PYTHONUNBUFFERED"
        value = "1"
      }
      env {
        name  = "GRAPH_GENERATOR_URL"
        value = google_cloud_run_v2_service.graph_generator.uri
      }
      env {
        name  = "CRM_SIMULATOR_URL"
        value = google_cloud_run_v2_service.crm_simulator.uri
      }
      env {
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = "gemini-api-key"
            version = "latest"
          }
        }
      }
      env {
        name  = "REDEPLOY_TRIGGER"
        value = "v5.0.0-ROLE-BASED-DASHBOARD"
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "1Gi"
        }
      }
    }

    timeout = "600s"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Public access for API
resource "google_cloud_run_v2_service_iam_member" "api_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ── Cloud Run: Graph Generator ───────────────────────────────────

resource "google_cloud_run_v2_service" "graph_generator" {
  name     = "synapse-graph-generator"
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.synapse_runner.email

    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/synapse/graph-generator:latest"

      ports {
        container_port = 8002
      }

      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "REGION"
        value = var.region
      }
      env {
        name  = "SKILL_GRAPHS_BUCKET"
        value = var.skill_graphs_bucket
      }
      env {
        name  = "PYTHONUNBUFFERED"
        value = "1"
      }
      env {
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = "gemini-api-key"
            version = "latest"
          }
        }
      }
      env {
        name  = "REDEPLOY_TRIGGER"
        value = "v4.3.0-LIVE-AUDIO-FIXES"
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }
    }

    timeout = "900s"  # Graph generation can take a few minutes
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Public access for Graph Generator (webhook target)
resource "google_cloud_run_v2_service_iam_member" "generator_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.graph_generator.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ── Cloud Run: CRM Simulator ────────────────────────────────────

resource "google_cloud_run_v2_service" "crm_simulator" {
  name     = "synapse-crm-simulator"
  location = var.region
  project  = var.project_id

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 1
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/synapse/crm-simulator:latest"

      ports {
        container_port = 8001
      }
      
      env {
        name  = "PYTHONUNBUFFERED"
        value = "1"
      }
      env {
        name  = "REDEPLOY_TRIGGER"
        value = "v3.7.0-GEMINI-2.5-UPGRADE"
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Public access for CRM Simulator
resource "google_cloud_run_v2_service_iam_member" "crm_simulator_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.crm_simulator.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ── Cloud Run: Hub — Tenant Config Portal ─────────────────────

resource "google_cloud_run_v2_service" "hub" {
  name     = "synapse-hub"
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.synapse_runner.email

    scaling {
      min_instance_count = 0
      max_instance_count = 1
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/synapse/hub:latest"

      ports {
        container_port = 8003
      }

      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "REGION"
        value = var.region
      }
      env {
        name  = "SKILL_GRAPHS_BUCKET"
        value = var.skill_graphs_bucket
      }
      env {
        name  = "PYTHONUNBUFFERED"
        value = "1"
      }
      env {
        name  = "GRAPH_GENERATOR_URL"
        value = google_cloud_run_v2_service.graph_generator.uri
      }
      env {
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = "gemini-api-key"
            version = "latest"
          }
        }
      }
      env {
        name  = "SYNAPSE_ADMIN_KEY"
        value = var.synapse_admin_key
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "1Gi"
        }
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Public access for Hub
resource "google_cloud_run_v2_service_iam_member" "hub_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.hub.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ── Cloud Run: Synapse Admin Portal ──────────────────────────

resource "google_cloud_run_v2_service" "admin" {
  name     = "synapse-admin"
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.synapse_runner.email

    scaling {
      min_instance_count = 0
      max_instance_count = 1
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/synapse/admin:latest"

      ports {
        container_port = 8004
      }

      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "PYTHONUNBUFFERED"
        value = "1"
      }
      env {
        name  = "SYNAPSE_ADMIN_KEY"
        value = var.synapse_admin_key
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "1Gi"
        }
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Public access for Admin Portal
resource "google_cloud_run_v2_service_iam_member" "admin_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.admin.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ── Outputs ──────────────────────────────────────────────────────

output "api_url" {
  value = google_cloud_run_v2_service.api.uri
}

output "graph_generator_url" {
  value = google_cloud_run_v2_service.graph_generator.uri
}

output "crm_simulator_url" {
  value = google_cloud_run_v2_service.crm_simulator.uri
}

output "hub_url" {
  value = google_cloud_run_v2_service.hub.uri
}

output "admin_url" {
  value = google_cloud_run_v2_service.admin.uri
}

output "artifact_registry" {
  value = google_artifact_registry_repository.synapse.name
}
