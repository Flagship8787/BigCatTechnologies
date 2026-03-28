output "workload_identity_provider" {
  description = "The full WIF provider resource name — use as GCP_WORKLOAD_IDENTITY_PROVIDER GitHub secret"
  value       = google_iam_workload_identity_pool_provider.github.name
}

output "service_account_email" {
  description = "The GitHub Actions service account email — use as GCP_SERVICE_ACCOUNT GitHub secret"
  value       = google_service_account.github_actions.email
}

output "registry_url" {
  description = "The Artifact Registry repository URL for Docker pushes"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.app.repository_id}"
}
