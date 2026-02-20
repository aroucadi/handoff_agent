output "skill_graphs_bucket" {
  description = "GCS bucket for skill graph files"
  value       = module.storage.skill_graphs_bucket_name
}

output "uploads_bucket" {
  description = "GCS bucket for contract PDF uploads"
  value       = module.storage.uploads_bucket_name
}

output "firestore_database" {
  description = "Firestore database name"
  value       = module.firestore.database_name
}
