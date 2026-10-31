terraform {
  required_version = ">= 1.6"

  required_providers {
    render = {
      source  = "render-oss/render"
      version = "~> 1.7"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 3.0"
    }
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.12"
    }
  }

  # Keep state remote so secrets (the Microsoft client secret) never live on a laptop. Example:
  # backend "azurerm" {
  #   resource_group_name  = "tfstate"
  #   storage_account_name = "indiasjourneytfstate"
  #   container_name       = "tfstate"
  #   key                  = "production.tfstate"
  # }
}

# Credentials come from the environment: RENDER_API_KEY + RENDER_OWNER_ID, ARM_TENANT_ID (+ az login or ARM_CLIENT_*),
# and GITHUB_TOKEN.
provider "render" {}

provider "azuread" {}

provider "github" {
  owner = var.github_owner
}

locals {
  # Predictable before the service exists, which avoids a Render <-> Azure dependency cycle.
  hostnames = concat(["${var.service_name}.onrender.com"], var.custom_domains)
  app_url   = "https://${local.hostnames[length(var.custom_domains) > 0 ? 1 : 0]}"
}

module "microsoft_oauth" {
  source          = "../../modules/azuread_oauth_app"
  count           = var.enable_microsoft ? 1 : 0
  display_name    = var.display_name
  hostnames       = local.hostnames
  allow_localhost = var.allow_localhost_redirects
}

module "web" {
  source = "../../modules/render_web_service"

  name             = var.service_name
  plan             = var.render_plan
  region           = var.render_region
  disk_size_gb     = var.disk_size_gb
  custom_domains   = var.custom_domains
  backup_site_url  = var.backup_site_url
  maintenance_mode = var.maintenance_mode

  # Google OAuth clients cannot be created with Terraform; create one in Google Cloud console (docs/AUTHENTICATION.md).
  google_client_id     = var.google_client_id
  google_client_secret = var.google_client_secret

  microsoft_client_id     = var.enable_microsoft ? module.microsoft_oauth[0].client_id : ""
  microsoft_client_secret = var.enable_microsoft ? module.microsoft_oauth[0].client_secret : ""
  microsoft_tenant        = var.enable_microsoft ? module.microsoft_oauth[0].tenant : "common"
}

module "github" {
  source                 = "../../modules/github_repository"
  owner                  = var.github_owner
  repository             = var.github_repository
  app_url                = local.app_url
  backup_site_url        = var.backup_site_url
  protect_default_branch = var.protect_default_branch
}
