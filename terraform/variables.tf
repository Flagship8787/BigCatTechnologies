variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "github_repo" {
  description = "The GitHub repository in org/repo format (e.g. BigCatTechnologies/bigcat-app)"
  type        = string
}

variable "db_password" {
  description = "Password for the Cloud SQL postgres user"
  type        = string
  sensitive   = true
}
