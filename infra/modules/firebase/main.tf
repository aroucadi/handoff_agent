# Firebase Hosting for Handoff frontend

variable "project_id" {
  type = string
}

resource "google_firebase_project" "handoff" {
  project = var.project_id
}

resource "google_firebase_web_app" "handoff" {
  project      = var.project_id
  display_name = "Handoff Voice Agent"

  depends_on = [google_firebase_project.handoff]
}

output "firebase_app_id" {
  value = google_firebase_web_app.handoff.app_id
}
