variable "name" {
  type        = string
  description = "Name of the Azure Cache for Redis."
}

variable "resource_group_name" {
  type        = string
  description = "Name of the Resource Group."
}

variable "location" {
  type        = string
  description = "Azure Region."
}

variable "sku_name" {
  type        = string
  description = "Pricing tier (Basic is lowest cost)."
  default     = "Basic"
}

variable "family" {
  type        = string
  description = "SKU Family (C = Basic/Standard)."
  default     = "C"
}

variable "capacity" {
  type        = number
  description = "Capacity (0 = 250MB, ~Rs. 1,200/mo)."
  default     = 0
}

variable "tags" {
  type        = map(string)
  description = "Resource tags."
  default     = {}
}
