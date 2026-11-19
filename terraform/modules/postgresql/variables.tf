variable "name" {
  type        = string
  description = "Name of the PostgreSQL Flexible Server."
}

variable "resource_group_name" {
  type        = string
  description = "Name of the Resource Group."
}

variable "location" {
  type        = string
  description = "Azure Region."
}

variable "admin_username" {
  type        = string
  description = "PostgreSQL administrator login username."
  default     = "ijadmin"
}

variable "admin_password" {
  type        = string
  description = "PostgreSQL administrator password."
  sensitive   = true
}

variable "sku_name" {
  type        = string
  description = "Burstable pricing tier (B_Standard_B1ms is the most economical ~Rs. 800/mo)."
  default     = "B_Standard_B1ms"
}

variable "tags" {
  type        = map(string)
  description = "Resource tags."
  default     = {}
}
