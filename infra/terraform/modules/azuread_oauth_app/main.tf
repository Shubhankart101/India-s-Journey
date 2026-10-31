terraform {
  required_version = ">= 1.6"
  required_providers {
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 3.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.12"
    }
  }
}

locals {
  # Microsoft Graph and its delegated User.Read permission (well-known IDs).
  graph_app_id   = "00000003-0000-0000-c000-000000000000"
  user_read_id   = "e1fe6dd8-ba31-4d61-89e7-88639da4683d"
  redirect_uris  = [for host in var.hostnames : "https://${host}/accounts/microsoft/login/callback/"]
  local_redirect = var.allow_localhost ? ["http://localhost:8000/accounts/microsoft/login/callback/"] : []
}

data "azuread_client_config" "current" {}

resource "azuread_application" "this" {
  display_name     = var.display_name
  sign_in_audience = var.sign_in_audience
  owners           = length(var.owners) > 0 ? var.owners : [data.azuread_client_config.current.object_id]

  # Personal Microsoft accounts (Outlook.com, Hotmail, Live) require v2 access tokens.
  api {
    requested_access_token_version = 2
  }

  web {
    homepage_url  = "https://${var.hostnames[0]}/"
    redirect_uris = concat(local.redirect_uris, local.local_redirect)

    implicit_grant {
      access_token_issuance_enabled = false
      id_token_issuance_enabled     = false
    }
  }

  required_resource_access {
    resource_app_id = local.graph_app_id

    resource_access {
      id   = local.user_read_id
      type = "Scope"
    }
  }
}

resource "time_rotating" "secret" {
  rotation_days = var.secret_rotation_days
}

resource "azuread_application_password" "this" {
  application_id = azuread_application.this.id
  display_name   = "django-allauth"
  end_date       = timeadd(time_rotating.secret.id, "${var.secret_rotation_days * 24 + 720}h")

  rotate_when_changed = {
    rotation = time_rotating.secret.id
  }
}
