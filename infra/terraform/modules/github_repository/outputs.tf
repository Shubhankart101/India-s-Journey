output "pages_url" {
  value = var.backup_site_url
}

output "repository_url" {
  value = data.github_repository.this.html_url
}
