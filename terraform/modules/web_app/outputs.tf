output "id" {
  description = "The ID of the Linux Web App."
  value       = azurerm_linux_web_app.app.id
}

output "name" {
  description = "The name of the Linux Web App."
  value       = azurerm_linux_web_app.app.name
}

output "default_hostname" {
  description = "The default hostname of the Web App."
  value       = azurerm_linux_web_app.app.default_hostname
}

output "default_url" {
  description = "The default HTTPS URL for the deployed Web App."
  value       = "https://${azurerm_linux_web_app.app.default_hostname}"
}
