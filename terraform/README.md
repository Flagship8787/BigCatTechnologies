# Terraform — GCP Infrastructure

Provisions the Google Cloud infrastructure required for the GitHub Actions Docker build/push workflow.

## What this provisions

- **Artifact Registry repository** (`bigcat-app`) — stores Docker images in `us-central1`
- **Workload Identity Federation** — keyless authentication so GitHub Actions can push images without long-lived service account keys
  - Workload Identity Pool: `github-pool`
  - Workload Identity Provider: `github-provider` (OIDC, issuer: `https://token.actions.githubusercontent.com`)
- **Service Account** (`github-actions-pusher`) — granted `roles/artifactregistry.writer` on the repository and `roles/run.developer` on the Cloud Run service
- **IAM binding** — allows the WIF pool to impersonate the service account for the configured GitHub repository
- **Cloud Run v2 service** (`bigcat-server`) — hosts the FastAPI/FastMCP Python server (port 3000) with public access, 0–3 instances, and a `/health` startup probe
- **Service Account** (`cloud-run-server`) — dedicated SA for the Cloud Run service, granted `roles/artifactregistry.reader` to pull images

## Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.9
- [gcloud CLI](https://cloud.google.com/sdk/docs/install) authenticated with sufficient IAM permissions
- The following GCP APIs enabled on your project:
  - `artifactregistry.googleapis.com`
  - `iam.googleapis.com`
  - `iamcredentials.googleapis.com`
  - `sts.googleapis.com`
  - `run.googleapis.com` (managed by Terraform via `google_project_service`)

## Usage

1. Copy the example vars file and fill in your values:

   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # edit terraform.tfvars
   ```

2. Initialize, plan, and apply:

   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

3. After apply, note the outputs — these map directly to your GitHub Actions secrets:

   | Terraform output              | GitHub Secret                      |
   |-------------------------------|------------------------------------|
   | `workload_identity_provider`  | `GCP_WORKLOAD_IDENTITY_PROVIDER`   |
   | `service_account_email`       | `GCP_SERVICE_ACCOUNT`              |
   | *(your GCP project ID)*       | `GCP_PROJECT_ID`                   |

   `GCP_PROJECT_ID` is not emitted as an output — use the same value you set in `terraform.tfvars`.

   The `cloud_run_url` output gives you the public URL of the deployed Cloud Run service.

## Security notes

- `terraform.tfvars` contains your project ID and **must not be committed**. It is listed in `.gitignore`.
- Workload Identity Federation means no service account key JSON is ever created or stored — authentication is ephemeral and scoped to the exact GitHub repository configured in `var.github_repo`.
