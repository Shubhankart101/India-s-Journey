output "id" {
  description = "The ID of the Redis Cache."
  value       = azurerm_redis_cache.redis.id
}

output "hostname" {
  description = "The Hostname of the Redis Cache."
  value       = azurerm_redis_cache.redis.hostname
}

output "ssl_port" {
  description = "The SSL Port of the Redis Cache."
  value       = azurerm_redis_cache.redis.ssl_port
}

output "primary_access_key" {
  description = "The Primary Access Key for the Redis Cache."
  value       = azurerm_redis_cache.redis.primary_access_key
  sensitive   = true
}

output "connection_string" {
  description = "The REDIS_URL formatted connection string with TLS."
  value       = "rediss://:${azurerm_redis_cache.redis.primary_access_key}@${azurerm_redis_cache.redis.hostname}:${azurerm_redis_cache.redis.ssl_port}/0"
  sensitive   = true
}
