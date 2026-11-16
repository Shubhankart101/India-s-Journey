variable "name" {
  type        = string
  description = "Name of the App Service Plan."
}

variable "resource_group_name" {
  type        = string
  description = "Name of the Resource Group in which to create the Service Plan."
}

variable "location" {
  type        = string
  description = "Azure Region for the Service Plan."
}

variable "os_type" {
  type        = string
  description = "Operating System type for the Service Plan (Linux or Windows)."
  default     = "Linux"
}

variable "sku_name" {
  type        = string
  description = "Compute pricing tier (B1, B2)."
  default     = "B1"

  validation {
    condition     = contains(["B1", "B2"], var.sku_name)
    error_message = "sku_name must be B1 or B2 to stay well within the monthly budget."
  }
}

variable "tags" {
  type        = map(string)
  description = "Tags to assign to the Service Plan."
  default     = {}
}
