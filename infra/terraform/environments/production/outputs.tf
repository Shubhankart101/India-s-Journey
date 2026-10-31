output "app_url" {
  value = module.web.url
}

output "backup_site_url" {
  value = var.backup_site_url
}

output "google_redirect_uris" {
  description = "Paste these into the Google Cloud OAuth client."
  value       = [for host in local.hostnames : "https://${host}/accounts/google/login/callback/"]
}

output "microsoft_redirect_uris" {
  value = var.enable_microsoft ? module.microsoft_oauth[0].redirect_uris : []
}

output "microsoft_client_id" {
  value = var.enable_microsoft ? module.microsoft_oauth[0].client_id : null
}
