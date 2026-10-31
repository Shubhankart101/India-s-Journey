mock_provider "github" {
  mock_data "github_repository" {
    defaults = {
      name           = "India-s-Journey"
      node_id        = "R_mock"
      default_branch = "main"
    }
  }
}

variables {
  owner      = "Shubhankart101"
  repository = "India-s-Journey"
  app_url    = "https://indias-journey.onrender.com"
}

run "sets_monitor_variables_and_outage_label" {
  command = plan

  assert {
    condition     = github_actions_variable.app_url.variable_name == "APP_URL" && github_actions_variable.app_url.value == "https://indias-journey.onrender.com"
    error_message = "The uptime monitor reads APP_URL."
  }

  assert {
    condition     = github_actions_variable.backup_site_url.value == "https://shubhankart101.github.io/India-s-Journey/"
    error_message = "BACKUP_SITE_URL defaults to GitHub Pages."
  }

  assert {
    condition     = github_issue_label.outage.name == "outage"
    error_message = "The uptime monitor files issues under the outage label."
  }

  assert {
    condition     = length(github_branch_protection.main) == 0 && length(github_actions_secret.this) == 0
    error_message = "Branch protection and secrets are opt-in."
  }
}

run "protects_branch_with_ci_checks" {
  command = plan

  variables {
    protect_default_branch = true
    actions_secrets        = { RENDER_DEPLOY_HOOK = "https://example.invalid/hook" }
  }

  assert {
    condition     = github_branch_protection.main[0].pattern == "main" && contains(github_branch_protection.main[0].required_status_checks[0].contexts, "Playwright end-to-end (desktop + mobile)")
    error_message = "The default branch must require the Web app CI checks."
  }

  assert {
    condition     = contains(keys(github_actions_secret.this), "RENDER_DEPLOY_HOOK")
    error_message = "Secrets are created per key."
  }
}
