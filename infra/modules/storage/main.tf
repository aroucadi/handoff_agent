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

# Knowledge Center bucket — static website for ClawdView docs
resource "google_storage_bucket" "knowledge_center" {
  name          = "${var.project_id}-knowledge-center"
  location      = var.region
  force_destroy = true
  project       = var.project_id

  uniform_bucket_level_access = true

  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }
  
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "OPTIONS"]
    response_header = ["Content-Type", "Access-Control-Allow-Origin"]
    max_age_seconds = 3600
  }
}

# Make Knowledge Center publicly readable
resource "google_storage_bucket_iam_member" "knowledge_center_public" {
  bucket = google_storage_bucket.knowledge_center.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
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

output "knowledge_center_bucket_name" {
  value = google_storage_bucket.knowledge_center.name
}

output "knowledge_center_bucket_url" {
  value = "https://storage.googleapis.com/${google_storage_bucket.knowledge_center.name}/index.html"
}
