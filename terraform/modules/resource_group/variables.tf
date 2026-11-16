variable "name" {
  type        = string
  description = "Name of the Azure Resource Group."
}

variable "location" {
  type        = string
  description = "Azure Region (e.g. centralindia, southindia)."
}

variable "tags" {
  type        = map(string)
  description = "Tags to assign to the Resource Group."
  default     = {}
}
