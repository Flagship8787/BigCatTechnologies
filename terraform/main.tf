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
  name                = "bigcat-client"
  location            = var.region
  ingress             = "INGRESS_TRAFFIC_ALL"
  deletion_protection = false

  # CI deploys new image revisions via gcloud — Terraform manages config only.
  lifecycle {
    ignore_changes = [template]
  }

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

# Allow GitHub Actions to act as the client Cloud Run service account (required for gcloud run deploy)
resource "google_service_account_iam_member" "github_actions_actAs_cloud_run_client" {
  service_account_id = google_service_account.cloud_run_client.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.github_actions.email}"
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
  name                = "bigcat-server"
  location            = var.region
  ingress             = "INGRESS_TRAFFIC_ALL"
  deletion_protection = false

  depends_on = [google_project_service.run]

  # CI deploys new image revisions via gcloud — Terraform manages config only.
  lifecycle {
    ignore_changes = [template]
  }

  template {
    service_account = google_service_account.cloud_run_server.email

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }

    # Attach Cloud SQL instance so the proxy socket is available
    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.postgres.connection_name]
      }
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

      # Database connection env vars for SQLAlchemy / asyncpg
      env {
        name  = "DB_HOST"
        value = "/cloudsql/${google_sql_database_instance.postgres.connection_name}"
      }
      env {
        name  = "DB_NAME"
        value = "bigcat"
      }
      env {
        name  = "DB_USER"
        value = "bigcat"
      }
      env {
        name = "DB_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.db_password.secret_id
            version = "latest"
          }
        }
      }

      # Redis (OAuthProxy cache)
      env {
        name  = "REDIS_HOST"
        value = var.redis_host
      }
      env {
        name  = "REDIS_PORT"
        value = var.redis_port
      }
      env {
        name  = "REDIS_USE_SSL"
        value = var.redis_use_ssl
      }
      env {
        name = "REDIS_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.redis_password.secret_id
            version = "latest"
          }
        }
      }

      # Auth0 (non-secret)
      env {
        name  = "AUTH0_JWKS_URI"
        value = var.auth0_jwks_uri
      }
      env {
        name  = "AUTH0_ISSUER"
        value = var.auth0_issuer
      }
      env {
        name  = "AUTH0_AUDIENCE"
        value = var.auth0_audience
      }
      env {
        name  = "AUTH0_AUTH_ENDPOINT"
        value = var.auth0_auth_endpoint
      }
      env {
        name  = "AUTH0_TOKEN_ENDPOINT"
        value = var.auth0_token_endpoint
      }
      env {
        name  = "AUTH0_CLIENT_ID"
        value = var.auth0_mcp_client_id
      }
      env {
        name = "AUTH0_CLIENT_SECRET"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.auth0_mcp_client_secret.secret_id
            version = "latest"
          }
        }
      }
      env {
        name  = "API_BASE_URL"
        value = var.api_base_url
      }
      env {
        name  = "AUTH0_REDIRECT_PATH"
        value = var.auth0_redirect_path
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
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

# Allow GitHub Actions to act as the server Cloud Run service account (required for gcloud run deploy)
resource "google_service_account_iam_member" "github_actions_actAs_cloud_run_server" {
  service_account_id = google_service_account.cloud_run_server.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.github_actions.email}"
}

# ---------------------------------------------------------------------------
# Cloud SQL — Postgres
# ---------------------------------------------------------------------------

# Enable required APIs
resource "google_project_service" "sqladmin" {
  service            = "sqladmin.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "secretmanager" {
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

# Cloud SQL Postgres instance
resource "google_sql_database_instance" "postgres" {
  name             = "bigcat-postgres"
  database_version = "POSTGRES_16"
  region           = var.region

  depends_on = [google_project_service.sqladmin]

  settings {
    tier              = "db-f1-micro"
    edition           = "ENTERPRISE"
    availability_type = "ZONAL"
    disk_size         = 10
    disk_autoresize   = true

    backup_configuration {
      enabled    = true
      start_time = "03:00"
    }

    ip_configuration {
      ipv4_enabled = true # Cloud Run connects via Auth Proxy socket, not the public IP
    }
  }

  deletion_protection = false
}

# Application database
resource "google_sql_database" "app" {
  name     = "bigcat"
  instance = google_sql_database_instance.postgres.name
}

# Application user
resource "google_sql_user" "app" {
  name     = "bigcat"
  instance = google_sql_database_instance.postgres.name
  password = var.db_password
}

# Store DB password in Secret Manager so Cloud Run can reference it
resource "google_secret_manager_secret" "db_password" {
  secret_id  = "bigcat-db-password"
  depends_on = [google_project_service.secretmanager]

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = var.db_password
}

# Grant Cloud Run server SA access to the secret
resource "google_secret_manager_secret_iam_member" "cloud_run_server_db_password" {
  secret_id = google_secret_manager_secret.db_password.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_server.email}"
}

# Store Auth0 MCP client secret in Secret Manager
resource "google_secret_manager_secret" "auth0_mcp_client_secret" {
  secret_id  = "bigcat-auth0-mcp-client-secret"
  depends_on = [google_project_service.secretmanager]

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "auth0_mcp_client_secret" {
  secret      = google_secret_manager_secret.auth0_mcp_client_secret.id
  secret_data = var.auth0_mcp_client_secret
}

resource "google_secret_manager_secret_iam_member" "cloud_run_server_auth0_mcp_client_secret" {
  secret_id = google_secret_manager_secret.auth0_mcp_client_secret.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_server.email}"
}

# Store Redis password in Secret Manager
resource "google_secret_manager_secret" "redis_password" {
  secret_id  = "bigcat-redis-password"
  depends_on = [google_project_service.secretmanager]

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "redis_password" {
  secret      = google_secret_manager_secret.redis_password.id
  secret_data = var.redis_password
}

resource "google_secret_manager_secret_iam_member" "cloud_run_server_redis_password" {
  secret_id = google_secret_manager_secret.redis_password.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_server.email}"
}

# Grant Cloud Run server SA Cloud SQL client access
resource "google_project_iam_member" "cloud_run_server_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run_server.email}"
}

# Output the instance connection name (needed for Cloud Run cloudsql annotation)
output "db_instance_connection_name" {
  value       = google_sql_database_instance.postgres.connection_name
  description = "Cloud SQL instance connection name for Cloud Run --add-cloudsql-instances"
}
