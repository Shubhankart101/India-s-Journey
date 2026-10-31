variable "display_name" {
  description = "Name shown on the Microsoft consent screen."
  type        = string
  default     = "India's Journey"
}

variable "hostnames" {
  description = "Public hostnames of the web app; each gets an /accounts/microsoft/login/callback/ redirect URI."
  type        = list(string)

  validation {
    condition     = length(var.hostnames) > 0
    error_message = "Provide at least one hostname."
  }
}

variable "sign_in_audience" {
  description = "AzureADandPersonalMicrosoftAccount allows Outlook.com/Hotmail/Live and work or school accounts (pair with MICROSOFT_TENANT=common)."
  type        = string
  default     = "AzureADandPersonalMicrosoftAccount"

  validation {
    condition     = contains(["AzureADMyOrg", "AzureADMultipleOrgs", "AzureADandPersonalMicrosoftAccount", "PersonalMicrosoftAccount"], var.sign_in_audience)
    error_message = "Unsupported sign_in_audience."
  }
}

variable "owners" {
  description = "Object IDs of the app registration owners."
  type        = list(string)
  default     = []
}

variable "allow_localhost" {
  description = "Also register http://localhost:8000 for local development."
  type        = bool
  default     = false
}

variable "secret_rotation_days" {
  description = "How often to rotate the client secret."
  type        = number
  default     = 180
}
