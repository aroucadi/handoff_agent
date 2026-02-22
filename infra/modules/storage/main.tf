resource "google_storage_bucket" "skill_graphs" {
  name          = "${var.project_id}-synapse-graphs"
  location      = var.region
  force_destroy = false
  project       = var.project_id

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD"]
    response_header = ["Content-Type"]
    max_age_seconds = 3600
  }
}

# Uploads bucket — stores contract PDFs and sales call transcripts
resource "google_storage_bucket" "uploads" {
  name          = "${var.project_id}-synapse-uploads"
  location      = var.region
  force_destroy = false
  project       = var.project_id

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
}

output "skill_graphs_bucket_name" {
  value = google_storage_bucket.skill_graphs.name
}

output "skill_graphs_bucket_url" {
  value = google_storage_bucket.skill_graphs.url
}

output "uploads_bucket_name" {
  value = google_storage_bucket.uploads.name
}

output "uploads_bucket_url" {
  value = google_storage_bucket.uploads.url
}
