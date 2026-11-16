variable "name" {
  type        = string
  description = "Name of the consumption budget."
}

variable "resource_group_id" {
  type        = string
  description = "The ID of the Resource Group to apply the budget to."
}

variable "amount" {
  type        = number
  description = "Budget ceiling amount in currency (e.g. INR)."
  default     = 12500
}

variable "contact_emails" {
  type        = list(string)
  description = "List of email addresses to receive alerts when spend exceeds 80% and 100%."
  default     = []
}
