variable "service_name" {
  type    = string
  default = "indias-journey"
}

variable "display_name" {
  type    = string
  default = "India's Journey"
}

variable "render_plan" {
  type    = string
  default = "starter"
}

variable "render_region" {
  type    = string
  default = "singapore"
}

variable "disk_size_gb" {
  type    = number
  default = 1
}

variable "custom_domains" {
  type    = list(string)
  default = []
}

variable "backup_site_url" {
  type    = string
  default = "https://shubhankart101.github.io/India-s-Journey/"
}

variable "maintenance_mode" {
  description = "Send all visitors to the GitHub Pages backup."
  type        = bool
  default     = false
}

variable "enable_microsoft" {
  description = "Create the Azure AD / Microsoft identity app registration for Outlook sign-in."
  type        = bool
  default     = true
}

variable "allow_localhost_redirects" {
  type    = bool
  default = false
}

variable "google_client_id" {
  type    = string
  default = ""
}

variable "google_client_secret" {
  type      = string
  default   = ""
  sensitive = true
}

variable "github_owner" {
  type    = string
  default = "Shubhankart101"
}

variable "github_repository" {
  type    = string
  default = "India-s-Journey"
}

variable "protect_default_branch" {
  type    = bool
  default = false
}
