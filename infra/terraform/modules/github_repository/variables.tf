variable "owner" {
  type    = string
  default = "Shubhankart101"
}

variable "repository" {
  type    = string
  default = "India-s-Journey"
}

variable "app_url" {
  description = "Public URL of the Django web app (monitored by the uptime workflow)."
  type        = string
}

variable "backup_site_url" {
  type    = string
  default = "https://shubhankart101.github.io/India-s-Journey/"
}

variable "actions_secrets" {
  description = "Repository Actions secrets, e.g. { RENDER_DEPLOY_HOOK_URL = \"...\" }."
  type        = map(string)
  default     = {}
  sensitive   = true
}

variable "protect_default_branch" {
  description = "Require the CI checks on the default branch. Off by default because the data pipelines push directly to main."
  type        = bool
  default     = false
}

variable "required_checks" {
  description = "Status check names (the job `name:` values in webapp-ci.yml) required before merging to the default branch."
  type        = list(string)
  default = [
    "Django tests + OpenAPI schema",
    "React unit tests + build",
    "Playwright end-to-end (desktop + mobile)",
    "Terraform fmt / validate / test",
  ]
}
