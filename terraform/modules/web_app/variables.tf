variable "name" {
  type        = string
  description = "Globally unique name for the Azure Linux Web App."
}

variable "resource_group_name" {
  type        = string
  description = "Name of the Resource Group."
}

variable "location" {
  type        = string
  description = "Azure Region for the Web App."
}

variable "service_plan_id" {
  type        = string
  description = "The ID of the App Service Plan."
}

variable "docker_image" {
  type        = string
  description = "Docker image tag without registry prefix (e.g. username/repo:latest)."
  default     = "shubhankart101/indias-journey:latest"
}

variable "docker_registry_url" {
  type        = string
  description = "URL of the container registry."
  default     = "https://ghcr.io"
}

variable "health_check_path" {
  type        = string
  description = "Endpoint path for App Service health check probes."
  default     = "/api/health/"
}

variable "app_settings" {
  type        = map(string)
  description = "Application settings (environment variables) for the container."
  default     = {}
}

variable "tags" {
  type        = map(string)
  description = "Tags to assign to the Web App."
  default     = {}
}
