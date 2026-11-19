output "id" {
  description = "The ID of the Azure Cognitive Account."
  value       = azurerm_cognitive_account.openai.id
}

output "endpoint" {
  description = "The endpoint URL for the Azure OpenAI service."
  value       = azurerm_cognitive_account.openai.endpoint
}

output "primary_access_key" {
  description = "The primary access key for the Azure OpenAI service."
  value       = azurerm_cognitive_account.openai.primary_access_key
  sensitive   = true
}

output "deployment_name" {
  description = "The name of the embedding deployment."
  value       = azurerm_cognitive_deployment.embedding.name
}
