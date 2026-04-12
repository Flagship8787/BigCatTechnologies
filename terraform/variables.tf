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

variable "redis_host" {
  description = "Redis host for OAuthProxy cache storage"
  type        = string
}

variable "redis_password" {
  description = "Password for the Redis instance"
  type        = string
  sensitive   = true
}

variable "redis_port" {
  description = "Redis port"
  type        = string
  default     = "6379"
}

variable "redis_use_ssl" {
  description = "Whether Redis connection uses SSL"
  type        = string
  default     = "false"
}

variable "auth0_domain" {
  description = "Auth0 tenant domain (e.g. your-tenant.us.auth0.com) — used by the React client"
  type        = string
}

variable "auth0_jwks_uri" {
  description = "Auth0 JWKS URI for JWT verification"
  type        = string
}

variable "auth0_issuer" {
  description = "Auth0 issuer URL"
  type        = string
}

variable "auth0_audience" {
  description = "Auth0 audience"
  type        = string
}

variable "auth0_auth_endpoint" {
  description = "Auth0 authorization endpoint"
  type        = string
}

variable "auth0_token_endpoint" {
  description = "Auth0 token endpoint"
  type        = string
}

variable "auth0_spa_client_id" {
  description = "Auth0 client ID for the React SPA frontend"
  type        = string
}

variable "auth0_spa_client_secret" {
  description = "Auth0 client secret for the React SPA (if applicable)"
  type        = string
  sensitive   = true
}

variable "auth0_mcp_client_id" {
  description = "Auth0 client ID for the MCP OAuth proxy (Regular Web Application)"
  type        = string
}

variable "auth0_mcp_client_secret" {
  description = "Auth0 client secret for the MCP OAuth proxy"
  type        = string
  sensitive   = true
}

variable "x_api_key" {
  description = "X (Twitter) API key"
  type        = string
  sensitive   = true
}

variable "x_api_key_secret" {
  description = "X (Twitter) API key secret"
  type        = string
  sensitive   = true
}

variable "x_access_token" {
  description = "X (Twitter) access token"
  type        = string
  sensitive   = true
}

variable "x_access_token_secret" {
  description = "X (Twitter) access token secret"
  type        = string
  sensitive   = true
}

variable "api_base_url" {
  description = "Public base URL of the API (used for OAuth redirect)"
  type        = string
}

variable "auth0_redirect_path" {
  description = "OAuth redirect path (e.g. /oauth/callback)"
  type        = string
  default     = "/oauth/callback"
}
