output "client_id" {
  description = "MICROSOFT_CLIENT_ID for the web app."
  value       = azuread_application.this.client_id
}

output "client_secret" {
  description = "MICROSOFT_CLIENT_SECRET for the web app."
  value       = azuread_application_password.this.value
  sensitive   = true
}

output "tenant" {
  description = "MICROSOFT_TENANT that matches the sign-in audience."
  value = lookup({
    AzureADMyOrg             = data.azuread_client_config.current.tenant_id
    AzureADMultipleOrgs      = "organizations"
    PersonalMicrosoftAccount = "consumers"
  }, var.sign_in_audience, "common")
}

output "redirect_uris" {
  value = azuread_application.this.web[0].redirect_uris
}
