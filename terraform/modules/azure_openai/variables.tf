variable "name" {
  type        = string
  description = "Name of the Azure OpenAI Cognitive Account."
}

variable "resource_group_name" {
  type        = string
  description = "Name of the Resource Group."
}

variable "location" {
  type        = string
  description = "Azure Region (e.g. eastus, swedencentral, or southcentralus where OpenAI is available)."
  default     = "eastus"
}

variable "deployment_name" {
  type        = string
  description = "Deployment name for the embedding model."
  default     = "text-embedding-3-small"
}

variable "tags" {
  type        = map(string)
  description = "Resource tags."
  default     = {}
}
