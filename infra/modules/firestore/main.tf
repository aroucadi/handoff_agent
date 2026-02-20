# Firestore Database for Handoff

resource "google_firestore_database" "handoff" {
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
  project     = var.project_id

  # Prevent accidental deletion
  deletion_policy = "ABANDON"
}

output "database_name" {
  value = google_firestore_database.handoff.name
}
