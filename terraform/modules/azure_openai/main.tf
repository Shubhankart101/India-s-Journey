resource "azurerm_cognitive_account" "openai" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "OpenAI"
  sku_name            = "S0"

  custom_subdomain_name = var.name

  tags = var.tags
}

resource "azurerm_cognitive_deployment" "embedding" {
  name                 = var.deployment_name
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "text-embedding-3-small"
    version = "1"
  }

  scale {
    type = "Standard"
  }
}
