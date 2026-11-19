variable "name" {
  type        = string
  description = "Name of the storage account (lowercase alphanumeric, 3-24 chars)."
}

variable "resource_group_name" {
  type        = string
  description = "Name of the parent resource group."
}

variable "location" {
  type        = string
  description = "Azure region."
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Resource tags."
}
