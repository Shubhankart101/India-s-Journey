output "web_app_url" {
  description = "The default HTTPS URL for the deployed web app."
  value       = module.web_app.default_url
}

output "web_app_name" {
  description = "Name of the Azure Web App."
  value       = module.web_app.name
}

output "resource_group_name" {
  description = "Azure Resource Group."
  value       = module.resource_group.name
}

output "service_plan_sku" {
  description = "Compute pricing tier."
  value       = module.service_plan.sku_name
}

output "estimated_monthly_cost" {
  description = "Estimated monthly compute cost."
  value       = var.sku_name == "B1" ? "Approx. Rs. 1,100 / month (~$13 USD)" : "Approx. Rs. 2,200 / month (~$26 USD)"
}

output "monthly_budget_ceiling" {
  description = "Configured budget ceiling in INR."
  value       = "Rs. ${var.monthly_budget_inr} / month"
}

output "database_configured" {
  description = "Whether a PostgreSQL database (Azure Flexible Server or external) is configured."
  value       = nonsensitive(local.effective_database_url != "")
}

output "redis_configured" {
  description = "Whether Redis cache (Azure Cache for Redis or external) is configured."
  value       = nonsensitive(local.effective_redis_url != "")
}

output "ai_endpoint_configured" {
  description = "Whether an Azure OpenAI or external AI endpoint is configured."
  value       = nonsensitive(local.effective_openai_endpoint != "")
}

output "postgresql_server_fqdn" {
  description = "FQDN of the Azure PostgreSQL server if provisioned."
  value       = length(module.postgresql) > 0 ? module.postgresql[0].fqdn : null
}

output "redis_hostname" {
  description = "Hostname of the Azure Cache for Redis if provisioned."
  value       = length(module.redis) > 0 ? module.redis[0].hostname : null
}

output "azure_openai_endpoint" {
  description = "Endpoint of the Azure OpenAI Cognitive Account if provisioned."
  value       = length(module.azure_openai) > 0 ? module.azure_openai[0].endpoint : null
}

output "storage_configured" {
  description = "Whether Azure Blob Storage is configured for pipeline data snapshots."
  value       = nonsensitive(local.effective_storage_connection_string != "")
}

output "storage_account_name" {
  description = "Name of the Azure Storage Account if provisioned."
  value       = length(module.storage) > 0 ? module.storage[0].storage_account_name : null
}

