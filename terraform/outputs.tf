output "web_app_url" {
  description = "The default HTTPS URL for the deployed web app."
  value       = "https://${azurerm_linux_web_app.app.default_hostname}"
}

output "web_app_name" {
  description = "Name of the Azure Web App."
  value       = azurerm_linux_web_app.app.name
}

output "resource_group_name" {
  description = "Azure Resource Group."
  value       = azurerm_resource_group.rg.name
}

output "service_plan_sku" {
  description = "Compute pricing tier."
  value       = azurerm_service_plan.plan.sku_name
}

output "estimated_monthly_cost" {
  description = "Estimated monthly compute cost."
  value       = var.sku_name == "B1" ? "Approx. Rs. 1,100 / month (~$13 USD)" : "Approx. Rs. 2,200 / month (~$26 USD)"
}

output "monthly_budget_ceiling" {
  description = "Configured budget ceiling in INR."
  value       = "Rs. ${var.monthly_budget_inr} / month"
}
