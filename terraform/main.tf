resource "random_string" "app_suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "random_password" "django_secret" {
  length  = 50
  special = true
}

locals {
  app_name   = "${var.app_name_prefix}-${random_string.app_suffix.result}"
  secret_key = var.django_secret_key != "" ? var.django_secret_key : random_password.django_secret.result

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

  app_settings = {
    WEBSITES_PORT                       = "8000"
    PORT                                = "8000"
    DJANGO_DEBUG                        = "false"
    DJANGO_SECRET_KEY                   = local.secret_key
    WEB_CONCURRENCY                     = var.web_concurrency
    GUNICORN_THREADS                    = var.gunicorn_threads
    DJANGO_SQLITE_PATH                  = "/home/data/db.sqlite3"
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = "true"
    DJANGO_LOG_LEVEL                    = "INFO"
  }
}

# Module 4: Consumption Budget Safeguard (Rs. 12,500 ceiling with email alerts)
module "budget" {
  source            = "./modules/budget"
  name              = "budget-${module.resource_group.name}"
  resource_group_id = module.resource_group.id
  amount            = var.monthly_budget_inr
  contact_emails    = var.budget_alert_emails
}
