output "id" {
  description = "The ID of the App Service Plan."
  value       = azurerm_service_plan.plan.id
}

output "name" {
  description = "The name of the App Service Plan."
  value       = azurerm_service_plan.plan.name
}

output "sku_name" {
  description = "The compute pricing tier."
  value       = azurerm_service_plan.plan.sku_name
}
