resource "azurerm_storage_account" "storage" {
  name                     = var.name
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  access_tier              = "Cool"
  min_tls_version          = "TLS1_2"

  tags = var.tags
}

resource "azurerm_storage_container" "datasets" {
  name                  = "datasets"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "pipeline_backups" {
  name                  = "pipeline-backups"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}
