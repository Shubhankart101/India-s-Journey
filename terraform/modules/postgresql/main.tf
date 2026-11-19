resource "azurerm_postgresql_flexible_server" "postgres" {
  name                   = var.name
  resource_group_name    = var.resource_group_name
  location               = var.location
  version                = "16"
  administrator_login    = var.admin_username
  administrator_password = var.admin_password
  storage_mb             = 32768
  sku_name               = var.sku_name

  tags = var.tags
}

resource "azurerm_postgresql_flexible_server_database" "database" {
  name      = "indias_journey"
  server_id = azurerm_postgresql_flexible_server.postgres.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# Allow Azure services and Web App to connect
resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_azure_services" {
  name             = "AllowAllAzureServicesAndResourcesWithinAzureIps"
  server_id        = azurerm_postgresql_flexible_server.postgres.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}
