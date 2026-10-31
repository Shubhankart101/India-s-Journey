output "id" {
  value = render_web_service.this.id
}

output "url" {
  description = "Public URL of the web app."
  value       = render_web_service.this.url
}

output "hostname" {
  value = trimprefix(render_web_service.this.url, "https://")
}
