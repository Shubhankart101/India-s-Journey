resource "azurerm_redis_cache" "redis" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  capacity              = var.capacity
  family                = var.family
  sku_name              = var.sku_name
  non_ssl_port_enabled  = false
  minimum_tls_version   = "1.2"

  redis_configuration {
    maxmemory_reserved = 10
    maxmemory_delta    = 10
    maxmemory_policy   = "allkeys-lru"
  }

  tags = var.tags
}
