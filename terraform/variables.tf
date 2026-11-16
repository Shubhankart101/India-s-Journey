variable "subscription_id" {
  type        = string
  description = "Azure Subscription ID to deploy resources into."
  default     = "1a264b52-6e39-4f81-a653-fbf2b8e98b10"
}

variable "resource_group_name" {
  type        = string
  description = "Name of the Azure Resource Group."
  default     = "rg-indiasjourney"
}

variable "location" {
  type        = string
  description = "Azure Region (centralindia = Pune, southindia = Chennai)."
  default     = "centralindia"
}

variable "app_name_prefix" {
  type        = string
  description = "Prefix for the globally unique Azure Web App name."
  default     = "indias-journey"
}

variable "sku_name" {
  type        = string
  description = "App Service Plan pricing tier: B1 (1 vCPU, 1.75GB RAM ~Rs. 1,100/mo) or B2 (2 vCPU, 3.5GB RAM ~Rs. 2,200/mo)."
  default     = "B1"

  validation {
    condition     = contains(["B1", "B2"], var.sku_name)
    error_message = "sku_name must be B1 or B2 to stay well within the Rs. 12,500/month budget."
  }
}

variable "docker_image" {
  type        = string
  description = "Full Docker container image tag (e.g. shubhankart101/indias-journey:latest or Azure Container Registry)."
  default     = "shubhankart101/indias-journey:latest"
}

variable "django_secret_key" {
  type        = string
  description = "Django SECRET_KEY. Leave blank to auto-generate a secure 50-character random string."
  default     = ""
  sensitive   = true
}

variable "monthly_budget_inr" {
  type        = number
  description = "Maximum monthly budget ceiling in Indian Rupees (INR)."
  default     = 12500
}

variable "budget_alert_emails" {
  type        = list(string)
  description = "List of email addresses to receive alerts when spend exceeds 80% and 100% of budget."
  default     = []
}

variable "web_concurrency" {
  type        = string
  description = "Number of Gunicorn worker processes (2 is ideal for 1.75 GB RAM on B1)."
  default     = "2"
}

variable "gunicorn_threads" {
  type        = string
  description = "Number of threads per Gunicorn worker (2 threads = 4 concurrent connections)."
  default     = "2"
}
