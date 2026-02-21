# Cloud Run Services for Handoff

# Artifact Registry repository for container images
resource "google_artifact_registry_repository" "handoff" {
  location      = var.region
  repository_id = "handoff"
  format        = "DOCKER"
  project       = var.project_id
}

# Service Account for Cloud Run services
resource "google_service_account" "handoff_runner" {
  account_id   = "handoff-runner"
  display_name = "Handoff Cloud Run Service Account"
  project      = var.project_id
}

# IAM: Cloud Run SA → GCS
resource "google_project_iam_member" "runner_gcs" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.handoff_runner.email}"
}

# IAM: Cloud Run SA → Firestore
resource "google_project_iam_member" "runner_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.handoff_runner.email}"
}

# IAM: Cloud Run SA → Secret Manager
resource "google_project_iam_member" "runner_secrets" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.handoff_runner.email}"
}

# ── Cloud Run: Handoff API ──────────────────────────────────────

resource "google_cloud_run_v2_service" "api" {
  name     = "handoff-api"
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.handoff_runner.email

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/handoff/api:latest"

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
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = "gemini-api-key"
            version = "latest"
          }
        }
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
  name     = "handoff-graph-generator"
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.handoff_runner.email

    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/handoff/graph-generator:latest"

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
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = "gemini-api-key"
            version = "latest"
          }
        }
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

# ── Outputs ──────────────────────────────────────────────────────

output "api_url" {
  value = google_cloud_run_v2_service.api.uri
}

output "graph_generator_url" {
  value = google_cloud_run_v2_service.graph_generator.uri
}

output "artifact_registry" {
  value = google_artifact_registry_repository.handoff.name
}
