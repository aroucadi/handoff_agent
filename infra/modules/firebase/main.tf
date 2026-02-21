# Firebase Hosting for Handoff frontend

variable "project_id" {
  type = string
}

resource "google_firebase_web_app" "handoff" {
  provider     = google
  project      = var.project_id
  display_name = "Handoff Voice Agent"
}

output "firebase_app_id" {
  value = google_firebase_web_app.handoff.app_id
}
