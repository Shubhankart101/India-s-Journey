terraform {
  required_version = ">= 1.6"
  required_providers {
    render = {
      source  = "render-oss/render"
      version = "~> 1.7"
    }
  }
}

locals {
  disk_path = "/var/data"

  base_env = {
    DJANGO_DEBUG      = { value = "false" }
    DJANGO_SECRET_KEY = { generate_value = true }
    BACKUP_SITE_URL   = { value = var.backup_site_url }
    BACKUP_STATUS_URL = { value = "${trimsuffix(var.backup_site_url, "/")}/status.html" }
    MICROSOFT_TENANT  = { value = var.microsoft_tenant }
  }

  # The onrender.com host is added automatically from RENDER_EXTERNAL_HOSTNAME.
  domain_env = length(var.custom_domains) == 0 ? {} : {
    DJANGO_ALLOWED_HOSTS        = { value = join(",", var.custom_domains) }
    DJANGO_CSRF_TRUSTED_ORIGINS = { value = join(",", [for domain in var.custom_domains : "https://${domain}"]) }
  }

  oauth_env = merge(
    var.google_client_id == "" ? {} : {
      GOOGLE_CLIENT_ID     = { value = var.google_client_id }
      GOOGLE_CLIENT_SECRET = { value = var.google_client_secret }
    },
    var.microsoft_client_id == "" ? {} : {
      MICROSOFT_CLIENT_ID     = { value = var.microsoft_client_id }
      MICROSOFT_CLIENT_SECRET = { value = var.microsoft_client_secret }
    },
  )

  disk_env = var.disk_size_gb > 0 ? { DJANGO_SQLITE_PATH = { value = "${local.disk_path}/db.sqlite3" } } : {}
}

resource "render_web_service" "this" {
  name              = var.name
  plan              = var.plan
  region            = var.region
  health_check_path = "/api/health/"

  runtime_source = {
    docker = {
      repo_url        = var.repo_url
      branch          = var.branch
      dockerfile_path = "./Dockerfile"
      context         = "."
      auto_deploy     = var.auto_deploy
      build_filter = {
        paths         = ["webapp/**", "frontend/**", "data/catalog.json", "Dockerfile"]
        ignored_paths = ["frontend/e2e/**", "**/tests/**", "docs/**"]
      }
    }
  }

  disk = var.disk_size_gb > 0 ? {
    name       = "${var.name}-data"
    size_gb    = var.disk_size_gb
    mount_path = local.disk_path
  } : null

  env_vars = merge(local.base_env, local.domain_env, local.oauth_env, local.disk_env, var.extra_env)

  custom_domains = length(var.custom_domains) > 0 ? [for domain in var.custom_domains : { name = domain }] : null

  # While enabled, Render redirects every request to the GitHub Pages backup.
  maintenance_mode = {
    enabled = var.maintenance_mode
    uri     = var.backup_site_url
  }

  notification_override = {
    notifications_to_send = "failure"
  }
}
