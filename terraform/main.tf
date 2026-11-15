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

  # Split docker image if registry is provided
  image_parts = split("/", var.docker_image)
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    Project     = "IndiasJourney"
    Environment = "Production"
    ManagedBy   = "Terraform"
    BudgetLimit = "INR-${var.monthly_budget_inr}"
  }
}

resource "azurerm_service_plan" "plan" {
  name                = "asp-${var.app_name_prefix}-${lower(var.sku_name)}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = var.sku_name

  tags = azurerm_resource_group.rg.tags
}

resource "azurerm_linux_web_app" "app" {
  name                = local.app_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id     = azurerm_service_plan.plan.id
  https_only          = true

  site_config {
    always_on                           = true
    http2_enabled                       = true
    minimum_tls_version                 = "1.2"
    health_check_path                   = "/api/health/"
    health_check_eviction_time_in_min   = 5

    application_stack {
      docker_image_name   = var.docker_image
      docker_registry_url = "https://ghcr.io"
    }
  }

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

  tags = azurerm_resource_group.rg.tags
}

# Cost Safeguard: Resource Group Monthly Budget Limit (Rs. 12,500)
resource "azurerm_consumption_budget_resource_group" "monthly_budget" {
  count             = length(var.budget_alert_emails) > 0 ? 1 : 0
  name              = "budget-${var.resource_group_name}"
  resource_group_id = azurerm_resource_group.rg.id
  amount            = var.monthly_budget_inr
  time_grain        = "Monthly"

  time_period {
    start_date = formatdate("YYYY-MM-01'T'00:00:00'Z'", timestamp())
  }

  notification {
    enabled        = true
    threshold      = 80.0
    operator       = "GreaterThan"
    threshold_type = "Actual"
    contact_emails = var.budget_alert_emails
  }

  notification {
    enabled        = true
    threshold      = 100.0
    operator       = "GreaterThan"
    threshold_type = "Actual"
    contact_emails = var.budget_alert_emails
  }
}
