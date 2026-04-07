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

output "cloud_run_url" {
  description = "The Cloud Run service URL"
  value       = google_cloud_run_v2_service.server.uri
}

output "client_registry_url" {
  description = "The Artifact Registry URL for the React client repo"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.client.repository_id}"
}

output "client_cloud_run_url" {
  description = "The Cloud Run URL for the React client service"
  value       = google_cloud_run_v2_service.client.uri
}

# ---------------------------------------------------------------------------
# GitHub Actions variable values for the React client build
# These are non-sensitive — set them as Actions *variables* (not secrets).
# After terraform apply, run: terraform output -json | jq '{...}'
# ---------------------------------------------------------------------------

output "vite_api_url" {
  description = "VITE_API_URL — GitHub Actions variable for the client Docker build"
  value       = var.api_base_url
}

output "vite_auth0_domain" {
  description = "VITE_AUTH0_DOMAIN — GitHub Actions variable for the client Docker build"
  value       = var.auth0_domain
}

output "vite_auth0_client_id" {
  description = "VITE_AUTH0_CLIENT_ID — GitHub Actions variable for the client Docker build"
  value       = var.auth0_spa_client_id
}

output "vite_auth0_audience" {
  description = "VITE_AUTH0_AUDIENCE — GitHub Actions variable for the client Docker build"
  value       = var.auth0_audience
}
