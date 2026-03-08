output "skill_graphs_bucket" {
  description = "GCS bucket for skill graph files"
  value       = module.storage.skill_graphs_bucket_name
}

output "uploads_bucket" {
  description = "GCS bucket for contract PDF uploads"
  value       = module.storage.uploads_bucket_name
}

output "knowledge_center_bucket" {
  description = "GCS bucket for ClawdView Knowledge Center"
  value       = module.storage.knowledge_center_bucket_name
}

output "knowledge_center_url" {
  description = "Public URL for ClawdView Knowledge Center"
  value       = module.storage.knowledge_center_bucket_url
}

output "firestore_database" {
  description = "Firestore database name"
  value       = module.firestore.database_name
}

output "api_url" {
  description = "Synapse API Cloud Run URL"
  value       = module.cloud_run.api_url
}

output "graph_generator_url" {
  description = "Graph Generator Cloud Run URL"
  value       = module.cloud_run.graph_generator_url
}

output "crm_simulator_url" {
  description = "SalesClaw CRM Simulator URL"
  value       = module.cloud_run.crm_simulator_url
}

output "hub_url" {
  description = "Hub Tenant Config Portal URL"
  value       = module.cloud_run.hub_url
}

output "admin_url" {
  description = "Synapse Admin Portal URL"
  value       = module.cloud_run.admin_url
}
