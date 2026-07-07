output "created_files" {
  value = [
    local_file.app_config.filename,
    local_file.nginx_config.filename,
    local_file.env_file.filename,
  ]
}

output "app_version" {
  value = "v1.0.0 — stable"
}
