output "created_files" {
  value = [
    local_file.app_config.filename,
    local_file.nginx_config.filename,
    local_file.env_file.filename,
    local_file.bad_new_resource.filename,
  ]
}

output "app_version" {
  value = "v2.0.0 — BROKEN (production is down!)"
}
