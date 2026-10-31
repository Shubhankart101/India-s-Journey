terraform {
  required_version = ">= 1.6"
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }
}

data "github_repository" "this" {
  full_name = "${var.owner}/${var.repository}"
}

# Read by .github/workflows/uptime-monitor.yml and docs/status.html links.
resource "github_actions_variable" "app_url" {
  repository    = data.github_repository.this.name
  variable_name = "APP_URL"
  value         = var.app_url
}

resource "github_actions_variable" "backup_site_url" {
  repository    = data.github_repository.this.name
  variable_name = "BACKUP_SITE_URL"
  value         = var.backup_site_url
}

resource "github_actions_secret" "this" {
  for_each        = nonsensitive(toset(keys(var.actions_secrets)))
  repository      = data.github_repository.this.name
  secret_name     = each.key
  plaintext_value = var.actions_secrets[each.key]
}

resource "github_issue_label" "outage" {
  repository  = data.github_repository.this.name
  name        = "outage"
  color       = "d73a4a"
  description = "Opened and closed automatically by the uptime monitor"
}

resource "github_branch_protection" "main" {
  count         = var.protect_default_branch ? 1 : 0
  repository_id = data.github_repository.this.node_id
  pattern       = data.github_repository.this.default_branch

  required_status_checks {
    strict   = false
    contexts = var.required_checks
  }

  allows_force_pushes = false
  allows_deletions    = false
}
