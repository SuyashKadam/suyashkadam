# ============================================================
# EXERCISE: State Recovery Practice
# Part 1 — v1 Initial Apply
#
# This uses the 'local' provider (no AWS needed).
# It creates files on your machine so you can see
# state tracking in action without any cloud cost.
# ============================================================

terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

# Simulates your "infrastructure" as local files.
# In real projects this would be aws_instance, aws_db_instance, etc.

resource "local_file" "app_config" {
  filename = "${path.module}/output/app.conf"
  content  = <<-EOT
    # App Configuration — Version 1
    APP_NAME=myapp
    APP_PORT=8080
    DB_HOST=prod-db.internal
    DB_PORT=5432
    MAX_CONNECTIONS=100
    CACHE_TTL=300
    ENVIRONMENT=production
    DEPLOY_VERSION=1.0.0
  EOT
}

resource "local_file" "nginx_config" {
  filename = "${path.module}/output/nginx.conf"
  content  = <<-EOT
    server {
        listen 80;
        server_name myapp.com;

        location / {
            proxy_pass http://localhost:8080;
            proxy_set_header Host $host;
        }

        # Health check endpoint
        location /health {
            return 200 "OK";
        }
    }
  EOT
}

resource "local_file" "env_file" {
  filename = "${path.module}/output/.env"
  content  = <<-EOT
    NODE_ENV=production
    API_KEY=safe-key-v1
    FEATURE_FLAG_NEW_UI=false
    FEATURE_FLAG_BETA_API=false
    LOG_LEVEL=info
  EOT
}
