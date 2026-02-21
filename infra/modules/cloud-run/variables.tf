variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "skill_graphs_bucket" {
  description = "GCS bucket name for skill graphs"
  type        = string
}

variable "uploads_bucket" {
  description = "GCS bucket name for uploads"
  type        = string
}
