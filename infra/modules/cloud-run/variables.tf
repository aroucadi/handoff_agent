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

variable "synapse_admin_key" {
  description = "The master admin key for Synapse"
  type        = string
  sensitive   = true
}

variable "demo_secret_key" {
  description = "The secret key for signing demo tokens"
  type        = string
  sensitive   = true
}

variable "deploy_tag" {
  description = "The container image tag to deploy (e.g. latest or timestamp)"
  type        = string
  default     = "latest"
}
