output "storage_account_name" {
  value       = azurerm_storage_account.storage.name
  description = "Storage account name."
}

output "primary_blob_endpoint" {
  value       = azurerm_storage_account.storage.primary_blob_endpoint
  description = "Primary blob endpoint URL."
}

output "primary_access_key" {
  value       = azurerm_storage_account.storage.primary_access_key
  sensitive   = true
  description = "Primary storage account access key."
}

output "connection_string" {
  value       = azurerm_storage_account.storage.primary_connection_string
  sensitive   = true
  description = "Primary connection string for blob storage."
}
