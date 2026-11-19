resource "random_string" "app_suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "random_password" "django_secret" {
  length  = 50
  special = true
}

resource "random_password" "postgres_secret" {
  count   = var.enable_postgresql && var.postgres_admin_password == "" ? 1 : 0
  length  = 24
  special = true
}

locals {
  app_name   = "${var.app_name_prefix}-${random_string.app_suffix.result}"
  secret_key = var.django_secret_key != "" ? var.django_secret_key : random_password.django_secret.result

  postgres_password = (
    var.postgres_admin_password != ""
    ? var.postgres_admin_password
    : (length(random_password.postgres_secret) > 0 ? random_password.postgres_secret[0].result : "")
  )

  effective_database_url = (
    var.enable_postgresql && length(module.postgresql) > 0
    ? module.postgresql[0].connection_string
    : var.external_database_url
  )

  effective_redis_url = (
    var.enable_azure_redis && length(module.redis) > 0
    ? module.redis[0].connection_string
    : var.external_redis_url
  )

  effective_openai_endpoint = (
    var.enable_azure_openai && length(module.azure_openai) > 0
    ? module.azure_openai[0].endpoint
    : var.external_azure_openai_endpoint
  )

  effective_openai_key = (
    var.enable_azure_openai && length(module.azure_openai) > 0
    ? module.azure_openai[0].primary_access_key
    : var.external_azure_openai_api_key
  )

  effective_openai_deployment = (
    var.enable_azure_openai && length(module.azure_openai) > 0
    ? module.azure_openai[0].deployment_name
    : "text-embedding-3-small"
  )

  effective_storage_connection_string = (
    var.enable_azure_storage && length(module.storage) > 0
    ? module.storage[0].connection_string
    : var.external_azure_storage_connection_string
  )

  effective_storage_account = (
    var.enable_azure_storage && length(module.storage) > 0
    ? module.storage[0].storage_account_name
    : var.external_azure_storage_account
  )

  common_tags = {
    Project     = "IndiasJourney"
    Environment = "Production"
    ManagedBy   = "Terraform"
    BudgetLimit = "INR-${var.monthly_budget_inr}"
  }
}

# Module 1: Resource Group
module "resource_group" {
  source   = "./modules/resource_group"
  name     = var.resource_group_name
  location = var.location
  tags     = local.common_tags
}

# Module 2: App Service Plan
module "service_plan" {
  source              = "./modules/service_plan"
  name                = "asp-${var.app_name_prefix}-${lower(var.sku_name)}"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  os_type             = "Linux"
  sku_name            = var.sku_name
  tags                = local.common_tags
}

# Optional Module 3A: Azure Database for PostgreSQL Flexible Server (Burstable B1ms)
module "postgresql" {
  count               = var.enable_postgresql ? 1 : 0
  source              = "./modules/postgresql"
  name                = "psql-${var.app_name_prefix}-${random_string.app_suffix.result}"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  admin_username      = var.postgres_admin_username
  admin_password      = local.postgres_password
  tags                = local.common_tags
}

# Optional Module 3B: Azure Cache for Redis (Basic C0)
module "redis" {
  count               = var.enable_azure_redis ? 1 : 0
  source              = "./modules/redis"
  name                = "redis-${var.app_name_prefix}-${random_string.app_suffix.result}"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  tags                = local.common_tags
}

# Optional Module 3C: Azure OpenAI Service (S0 pay-as-you-go)
module "azure_openai" {
  count               = var.enable_azure_openai ? 1 : 0
  source              = "./modules/azure_openai"
  name                = "oai-${var.app_name_prefix}-${random_string.app_suffix.result}"
  resource_group_name = module.resource_group.name
  location            = var.azure_openai_location
  deployment_name     = "text-embedding-3-small"
  tags                = local.common_tags
}

# Optional Module 3D: Azure Storage Account (Standard LRS Cool tier for dataset archival)
module "storage" {
  count               = var.enable_azure_storage ? 1 : 0
  source              = "./modules/storage"
  name                = substr("st${replace(var.app_name_prefix, "-", "")}${random_string.app_suffix.result}", 0, 24)
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  tags                = local.common_tags
}

# Module 3: Linux Web App
module "web_app" {
  source              = "./modules/web_app"
  name                = local.app_name
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  service_plan_id     = module.service_plan.id
  docker_image        = var.docker_image
  docker_registry_url = "https://ghcr.io"
  health_check_path   = "/api/health/"
  tags                = local.common_tags

  app_settings = merge(
    {
      WEBSITES_PORT                       = "8000"
      PORT                                = "8000"
      DJANGO_DEBUG                        = "false"
      DJANGO_SECRET_KEY                   = local.secret_key
      WEB_CONCURRENCY                     = var.web_concurrency
      GUNICORN_THREADS                    = var.gunicorn_threads
      DJANGO_SQLITE_PATH                  = "/home/data/db.sqlite3"
      WEBSITES_ENABLE_APP_SERVICE_STORAGE = "true"
      DJANGO_LOG_LEVEL                    = "INFO"
    },
    local.effective_database_url != "" ? { DATABASE_URL = local.effective_database_url } : {},
    local.effective_redis_url != "" ? { REDIS_URL = local.effective_redis_url } : {},
    var.google_client_id != "" ? {
      GOOGLE_CLIENT_ID     = var.google_client_id
      GOOGLE_CLIENT_SECRET = var.google_client_secret
    } : {},
    var.microsoft_client_id != "" ? {
      MICROSOFT_CLIENT_ID     = var.microsoft_client_id
      MICROSOFT_CLIENT_SECRET = var.microsoft_client_secret
      MICROSOFT_TENANT        = var.microsoft_tenant
    } : {},
    local.effective_openai_endpoint != "" ? {
      AZURE_OPENAI_ENDPOINT             = local.effective_openai_endpoint
      AZURE_OPENAI_API_KEY              = local.effective_openai_key
      AZURE_OPENAI_EMBEDDING_DEPLOYMENT = local.effective_openai_deployment
    } : {},
    local.effective_storage_connection_string != "" ? {
      AZURE_STORAGE_CONNECTION_STRING = local.effective_storage_connection_string
      AZURE_STORAGE_ACCOUNT           = local.effective_storage_account
    } : {}
  )
}


# Module 4: Consumption Budget Safeguard (Rs. 12,500 ceiling with email alerts)
module "budget" {
  source            = "./modules/budget"
  name              = "budget-${module.resource_group.name}"
  resource_group_id = module.resource_group.id
  amount            = var.monthly_budget_inr
  contact_emails    = var.budget_alert_emails
}
