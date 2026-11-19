variable "subscription_id" {
  type        = string
  description = "Azure Subscription ID to deploy resources into."
  default     = "1a264b52-6e39-4f81-a653-fbf2b8e98b10"
}

variable "resource_group_name" {
  type        = string
  description = "Name of the Azure Resource Group."
  default     = "rg-indiasjourney"
}

variable "location" {
  type        = string
  description = "Azure Region (centralindia = Pune, southindia = Chennai)."
  default     = "centralindia"
}

variable "app_name_prefix" {
  type        = string
  description = "Prefix for the globally unique Azure Web App name."
  default     = "indias-journey"
}

variable "sku_name" {
  type        = string
  description = "App Service Plan pricing tier: B1 (1 vCPU, 1.75GB RAM ~Rs. 1,100/mo) or B2 (2 vCPU, 3.5GB RAM ~Rs. 2,200/mo)."
  default     = "B1"

  validation {
    condition     = contains(["B1", "B2"], var.sku_name)
    error_message = "sku_name must be B1 or B2 to stay well within the Rs. 12,500/month budget."
  }
}

variable "docker_image" {
  type        = string
  description = "Full Docker container image tag (e.g. shubhankart101/indias-journey:latest or Azure Container Registry)."
  default     = "shubhankart101/indias-journey:latest"
}

variable "django_secret_key" {
  type        = string
  description = "Django SECRET_KEY. Leave blank to auto-generate a secure 50-character random string."
  default     = ""
  sensitive   = true
}

variable "monthly_budget_inr" {
  type        = number
  description = "Maximum monthly budget ceiling in Indian Rupees (INR)."
  default     = 12500
}

variable "budget_alert_emails" {
  type        = list(string)
  description = "List of email addresses to receive alerts when spend exceeds 80% and 100% of budget."
  default     = []
}

variable "web_concurrency" {
  type        = string
  description = "Number of Gunicorn worker processes (2 is ideal for 1.75 GB RAM on B1)."
  default     = "2"
}

variable "gunicorn_threads" {
  type        = string
  description = "Number of threads per Gunicorn worker (2 threads = 4 concurrent connections)."
  default     = "2"
}

# --- Database Configuration (PostgreSQL / SQLite) ---

variable "enable_postgresql" {
  type        = bool
  description = "Provision an Azure Database for PostgreSQL Flexible Server (Burstable B1ms ~Rs. 800/mo). Default false (uses zero-cost WAL SQLite)."
  default     = false
}

variable "postgres_admin_username" {
  type        = string
  description = "Admin username for PostgreSQL Flexible Server."
  default     = "ijadmin"
}

variable "postgres_admin_password" {
  type        = string
  description = "Admin password for PostgreSQL Flexible Server. Auto-generated if left blank."
  default     = ""
  sensitive   = true
}

variable "external_database_url" {
  type        = string
  description = "External PostgreSQL connection string (e.g. Neon or Supabase free tier). Overridden by enable_postgresql if true."
  default     = ""
  sensitive   = true
}

# --- Cache Configuration (Redis / LocMemCache) ---

variable "enable_azure_redis" {
  type        = bool
  description = "Provision an Azure Cache for Redis (Basic C0 ~Rs. 1,200/mo). Default false (uses zero-cost in-memory LocMemCache)."
  default     = false
}

variable "external_redis_url" {
  type        = string
  description = "External Redis connection URL (e.g. Upstash Redis free tier rediss://... or Redis Cloud). Overridden by enable_azure_redis if true."
  default     = ""
  sensitive   = true
}

# --- AI & Cognitive Services Configuration ---

variable "enable_azure_openai" {
  type        = bool
  description = "Provision an Azure OpenAI Cognitive Account with text-embedding-3-small deployment. Default false (uses zero-cost in-memory vectorizer)."
  default     = false
}

variable "azure_openai_location" {
  type        = string
  description = "Azure region for OpenAI (e.g. eastus, swedencentral)."
  default     = "eastus"
}

variable "external_azure_openai_endpoint" {
  type        = string
  description = "Pre-existing Azure OpenAI endpoint (e.g. https://my-openai.openai.azure.com/)."
  default     = ""
}

variable "external_azure_openai_api_key" {
  type        = string
  description = "Pre-existing Azure OpenAI API key."
  default     = ""
  sensitive   = true
}

# --- OAuth Authentication Credentials (Google & Microsoft) ---

variable "google_client_id" {
  type        = string
  description = "Google OAuth 2.0 Web Application Client ID."
  default     = ""
}

variable "google_client_secret" {
  type        = string
  description = "Google OAuth 2.0 Web Application Client Secret."
  default     = ""
  sensitive   = true
}

variable "microsoft_client_id" {
  type        = string
  description = "Microsoft Entra ID / App Registration Client ID."
  default     = ""
}

variable "microsoft_client_secret" {
  type        = string
  description = "Microsoft Entra ID / App Registration Client Secret."
  default     = ""
  sensitive   = true
}

variable "microsoft_tenant" {
  type        = string
  description = "Microsoft OAuth tenant (common accepts Outlook/Hotmail/Live and work accounts)."
  default     = "common"
}

# --- Azure Blob Storage Configuration (Data Pipelines & Archival) ---

variable "enable_azure_storage" {
  type        = bool
  description = "Provision an Azure Storage Account (Standard LRS, Cool tier ~Rs. 60/mo) for pipeline data snapshots and indicator backups."
  default     = false
}

variable "external_azure_storage_connection_string" {
  type        = string
  description = "External or existing Azure Storage Account connection string."
  default     = ""
  sensitive   = true
}

variable "external_azure_storage_account" {
  type        = string
  description = "External or existing Azure Storage Account name."
  default     = ""
}


