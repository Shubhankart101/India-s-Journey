output "id" {
  description = "The ID of the consumption budget (if created)."
  value       = try(azurerm_consumption_budget_resource_group.budget[0].id, null)
}

output "name" {
  description = "The name of the consumption budget (if created)."
  value       = try(azurerm_consumption_budget_resource_group.budget[0].name, null)
}
