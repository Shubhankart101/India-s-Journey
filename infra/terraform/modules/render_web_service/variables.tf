variable "name" {
  description = "Render service name (also the default onrender.com subdomain)."
  type        = string
  default     = "indias-journey"
}

variable "plan" {
  description = "Render plan. Persistent disks need a paid plan such as starter."
  type        = string
  default     = "starter"
}

variable "region" {
  description = "One of frankfurt, ohio, oregon, singapore, virginia."
  type        = string
  default     = "singapore"

  validation {
    condition     = contains(["frankfurt", "ohio", "oregon", "singapore", "virginia"], var.region)
    error_message = "Unsupported Render region."
  }
}

variable "repo_url" {
  description = "Git repository Render builds from."
  type        = string
  default     = "https://github.com/Shubhankart101/India-s-Journey"
}

variable "branch" {
  type    = string
  default = "main"
}

variable "auto_deploy" {
  type    = bool
  default = true
}

variable "disk_size_gb" {
  description = "Persistent disk for SQLite (keeps accounts and saved charts across deploys). 0 = no disk (data resets on deploy)."
  type        = number
  default     = 1
}

variable "custom_domains" {
  description = "Optional custom hostnames. The onrender.com host is always allowed via RENDER_EXTERNAL_HOSTNAME."
  type        = list(string)
  default     = []
}

variable "backup_site_url" {
  description = "Static GitHub Pages mirror linked from error pages and used as the maintenance redirect."
  type        = string
  default     = "https://shubhankart101.github.io/India-s-Journey/"
}

variable "maintenance_mode" {
  description = "Redirect all traffic to the backup site."
  type        = bool
  default     = false
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

variable "microsoft_client_id" {
  type    = string
  default = ""
}

variable "microsoft_client_secret" {
  type      = string
  default   = ""
  sensitive = true
}

variable "microsoft_tenant" {
  description = "common (work + personal Outlook accounts), consumers, organizations, or a tenant ID."
  type        = string
  default     = "common"
}

variable "extra_env" {
  description = "Additional environment variables: { NAME = { value = \"...\" } }."
  type = map(object({
    value          = optional(string)
    generate_value = optional(bool)
  }))
  default = {}
}
