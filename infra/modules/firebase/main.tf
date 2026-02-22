# Firebase Hosting for Synapse frontend

variable "project_id" {
  type = string
}

resource "google_firebase_project" "synapse" {
  provider = google-beta
  project = var.project_id
}

resource "google_firebase_web_app" "synapse" {
  provider     = google-beta
  project      = var.project_id
  display_name = "Synapse Voice Agent"

  depends_on = [google_firebase_project.synapse]
}

output "firebase_app_id" {
  value = google_firebase_web_app.synapse.app_id
}
