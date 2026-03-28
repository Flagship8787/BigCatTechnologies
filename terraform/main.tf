terraform {
  required_version = ">= 1.9"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Artifact Registry repository
resource "google_artifact_registry_repository" "app" {
  location      = var.region
  repository_id = "bigcat-app"
  description   = "BigCat Technologies application images"
  format        = "DOCKER"
}

# Workload Identity Pool
resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "github-pool"
  display_name              = "GitHub Actions Pool"
}

# Workload Identity Provider
resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  display_name                       = "GitHub Actions Provider"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
    "attribute.actor"      = "assertion.actor"
  }

  attribute_condition = "attribute.repository == \"${var.github_repo}\""

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# Service Account for GitHub Actions
resource "google_service_account" "github_actions" {
  account_id   = "github-actions-pusher"
  display_name = "GitHub Actions - Artifact Registry Pusher"
}

# Grant service account Artifact Registry writer on the repository
resource "google_artifact_registry_repository_iam_member" "github_actions_writer" {
  location   = google_artifact_registry_repository.app.location
  repository = google_artifact_registry_repository.app.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.github_actions.email}"
}

# Allow the Workload Identity Pool to impersonate the service account
resource "google_service_account_iam_member" "github_wif_binding" {
  service_account_id = google_service_account.github_actions.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_repo}"
}

# ---------------------------------------------------------------------------
# React Client — Artifact Registry, Cloud Run, IAM
# ---------------------------------------------------------------------------

# Artifact Registry repository for the React client image
resource "google_artifact_registry_repository" "client" {
  location      = var.region
  repository_id = "bigcat-client"
  description   = "BigCat Technologies React client images"
  format        = "DOCKER"
}

# Service account for the client Cloud Run service
resource "google_service_account" "cloud_run_client" {
  account_id   = "cloud-run-client"
  display_name = "Cloud Run - Client"
}

# Grant the client service account read access to the client registry
resource "google_artifact_registry_repository_iam_member" "cloud_run_client_reader" {
  location   = google_artifact_registry_repository.client.location
  repository = google_artifact_registry_repository.client.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.cloud_run_client.email}"
}

# Cloud Run v2 service for the React client
resource "google_cloud_run_v2_service" "client" {
  name     = "bigcat-client"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.cloud_run_client.email

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }

    containers {
      image = "us-central1-docker.pkg.dev/${var.project_id}/bigcat-client/client:latest"

      ports {
        container_port = 80
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }
  }
}

# Allow unauthenticated (public) access to the client service
resource "google_cloud_run_v2_service_iam_member" "client_public" {
  project  = google_cloud_run_v2_service.client.project
  location = google_cloud_run_v2_service.client.location
  name     = google_cloud_run_v2_service.client.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Grant GitHub Actions pusher the ability to deploy the client service
resource "google_cloud_run_v2_service_iam_member" "github_actions_client_developer" {
  project  = google_cloud_run_v2_service.client.project
  location = google_cloud_run_v2_service.client.location
  name     = google_cloud_run_v2_service.client.name
  role     = "roles/run.developer"
  member   = "serviceAccount:${google_service_account.github_actions.email}"
}

# Enable Cloud Run API
resource "google_project_service" "run" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

# Service Account for Cloud Run
resource "google_service_account" "cloud_run_server" {
  account_id   = "cloud-run-server"
  display_name = "Cloud Run - Server"
}

# Grant Cloud Run SA pull access to Artifact Registry
resource "google_artifact_registry_repository_iam_member" "cloud_run_reader" {
  location   = google_artifact_registry_repository.app.location
  repository = google_artifact_registry_repository.app.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.cloud_run_server.email}"
}

# Cloud Run v2 Service
resource "google_cloud_run_v2_service" "server" {
  name     = "bigcat-server"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  depends_on = [google_project_service.run]

  template {
    service_account = google_service_account.cloud_run_server.email

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }

    containers {
      image = "us-central1-docker.pkg.dev/${var.project_id}/bigcat-app/server:latest"

      ports {
        container_port = 3000
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      startup_probe {
        initial_delay_seconds = 5
        http_get {
          path = "/health"
          port = 3000
        }
      }
    }
  }
}

# Allow unauthenticated invocations
resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  name     = google_cloud_run_v2_service.server.name
  location = google_cloud_run_v2_service.server.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Grant github-actions-pusher the Cloud Run developer role for CI deployments
resource "google_cloud_run_v2_service_iam_member" "github_actions_deployer" {
  name     = google_cloud_run_v2_service.server.name
  location = google_cloud_run_v2_service.server.location
  role     = "roles/run.developer"
  member   = "serviceAccount:${google_service_account.github_actions.email}"
}
