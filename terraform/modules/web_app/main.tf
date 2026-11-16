resource "azurerm_linux_web_app" "app" {
  name                = var.name
  resource_group_name = var.resource_group_name
  location            = var.location
  service_plan_id     = var.service_plan_id
  https_only          = true

  site_config {
    always_on                         = true
    http2_enabled                     = true
    minimum_tls_version               = "1.2"
    health_check_path                 = var.health_check_path
    health_check_eviction_time_in_min = 5

    application_stack {
      docker_image_name   = var.docker_image
      docker_registry_url = var.docker_registry_url
    }
  }

  app_settings = var.app_settings
  tags         = var.tags
}
