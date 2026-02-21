# Firestore Database for Handoff

resource "google_firestore_database" "handoff" {
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
  project     = var.project_id

  # Prevent accidental deletion
  deletion_policy = "ABANDON"
}

# Vector Index for R8 Skill Graph 'FindNearest' Search
resource "google_firestore_index" "skill_graph_vector_index" {
  project    = var.project_id
  database   = google_firestore_database.handoff.name
  collection = "nodes" # Collection group name

  fields {
    field_path = "embedding"
    vector_config {
      dimension = 768
      flat {}
    }
  }
}

output "database_name" {
  value = google_firestore_database.handoff.name
}
