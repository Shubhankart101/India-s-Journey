output "id" {
  description = "The ID of the PostgreSQL Flexible Server."
  value       = azurerm_postgresql_flexible_server.postgres.id
}

output "fqdn" {
  description = "The FQDN of the PostgreSQL Flexible Server."
  value       = azurerm_postgresql_flexible_server.postgres.fqdn
}

output "database_name" {
  description = "The name of the database."
  value       = azurerm_postgresql_flexible_server_database.database.name
}

output "connection_string" {
  description = "The DATABASE_URL connection string formatted for Django/dj-database-url."
  value       = "postgresql://${var.admin_username}:${var.admin_password}@${azurerm_postgresql_flexible_server.postgres.fqdn}:5432/${azurerm_postgresql_flexible_server_database.database.name}?sslmode=require"
  sensitive   = true
}
